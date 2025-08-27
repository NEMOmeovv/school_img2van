from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
import requests

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True               
            user.is_approved = False            
            user.save()
            messages.success(request, '가입 신청이 완료되었습니다. 관리자의 승인 후 로그인할 수 있습니다.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'profiles/signup.html', {'form': form})

class CustomLoginView(LoginView):
    def form_valid(self, form):
        user = form.get_user()
        if not user.is_approved:
            messages.error(self.request, "관리자의 승인 대기 중입니다.")
            return redirect('login')  # 로그인 페이지로 다시 이동
        return super().form_valid(form)
    



User = get_user_model()

# 관리자인 경우에만 접근 허용
def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def approve_users_view(request):
    pending_users = User.objects.filter(is_approved=False)
    return render(request, 'profiles/approve_users.html', {'pending_users': pending_users})

@user_passes_test(is_admin)
def approve_user_action(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f"{user.username} 님이 승인되었습니다.")
    return redirect('approve_users')

# 큐 내용 미리보기 (미완성)
@user_passes_test(is_admin)
def comfy_queue_view(request):
    try:
        response = requests.get('http://127.0.0.1:8188/queue', timeout=5)
        queue_data = response.json()
    except Exception as e:
        queue_data = {'error': str(e)}

    return render(request, 'profiles/comfy_queue.html', {'queue': queue_data})

