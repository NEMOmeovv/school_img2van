from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=50)
    school = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    is_approved = models.BooleanField(default=False)  # 관리자가 승인해야 True

    def __str__(self):
        return self.username
