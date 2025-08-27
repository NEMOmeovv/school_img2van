import os
from io import BytesIO
import json
import shutil
import time
import requests
from pathlib import Path
from datetime import datetime
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from PIL import Image
import pprint

def generate_modified_workflow(image_filename):
    base_prefix = Path(image_filename).stem + "_output"

    with open('gogh_api.json', 'r', encoding='utf-8') as f:
        prompt = json.load(f)

    if "10" in prompt:
        prompt["10"]["inputs"]["image"] = image_filename
        print("10101010_filename:",image_filename)

    if "14" in prompt:
        prompt["14"]["inputs"]["filename_prefix"] = base_prefix
        # 덮어쓰기 및 단일 이미지 저장 설정
        prompt["14"]["inputs"]["overwrite"] = True
        prompt["14"]["inputs"]["extension"] = "png"
        prompt["14"]["inputs"]["save_as_grid"] = False
        print("141414141414_baseprefix:",base_prefix)

    return {"prompt": prompt}

def wait_for_output_image(base_filename, timeout=15):
    output_prefix = Path(base_filename).stem + "_output"
    output_dir = Path('C:/Users/jung1/CodingProjects/ComfyUI_windows_portable/ComfyUI/output')

    before_files = set(os.listdir(output_dir))  # 기존 파일 목록

    for _ in range(timeout):
        time.sleep(1)
        current_files = set(os.listdir(output_dir))
        new_files = current_files - before_files

        for filename in new_files:
            if filename.startswith(output_prefix) and filename.endswith(".png"):
                result_file = output_dir / filename

                destination_dir = Path(settings.MEDIA_ROOT) / 'outputs'
                destination_dir.mkdir(parents=True, exist_ok=True)
                destination_path = destination_dir / result_file.name
                shutil.copy(result_file, destination_path)

                return f'outputs/{result_file.name}'

    return None



@login_required
def img2img_view(request):
    if not request.user.is_approved:
        messages.warning(request, "아직 관리자의 승인이 완료되지 않았습니다.")
        return redirect('login')

    if request.method == 'POST':
        input_image = request.FILES.get('input_image')
        print(f"input_image: {input_image}")
        if not input_image:
            return render(request, 'img2img/upload.html', {'error': '이미지 파일이 업로드되지 않았습니다.'})

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{input_image}_{timestamp}.png"

        img_bytes = BytesIO(input_image.read())
        image = Image.open(img_bytes).convert("RGB")

        upload_path = Path(settings.MEDIA_ROOT) / 'uploads'
        upload_path.mkdir(parents=True, exist_ok=True)
        django_image_path = upload_path / base_filename
        image.save(django_image_path, "PNG")

        comfy_input_dir = Path('C:/Users/jung1/CodingProjects/ComfyUI_windows_portable/ComfyUI/input')
        comfy_input_dir.mkdir(parents=True, exist_ok=True)
        comfy_image_path = comfy_input_dir / base_filename
        shutil.copy(django_image_path, comfy_image_path)

        time.sleep(1)

        try:
            workflow = generate_modified_workflow(base_filename)
            print(type(workflow))
            pprint.pprint(workflow, width=120)

            response = requests.post(
                'http://127.0.0.1:8188/prompt',
                json=workflow,
                timeout=60
            )

            if response.status_code == 200:
                result_path = wait_for_output_image(base_filename)
                if result_path:
                    return render(request, 'img2img/upload.html', {
                        'result_image': result_path
                    })
                else:
                    return render(request, 'img2img/upload.html', {
                        'error': '결과 이미지를 찾을 수 없습니다.'
                    })
            else:
                return render(request, 'img2img/upload.html', {
                    'error': f'ComfyUI 응답 실패: 상태 코드 {response.status_code}'
                })

        except Exception as e:
            return render(request, 'img2img/upload.html', {
                'error': f'에러 발생: {str(e)}'
            })

    return render(request, 'img2img/upload.html')
