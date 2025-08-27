from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'full_name', 'school', 'phone', 'is_approved', 'is_staff')
    list_filter = ('is_approved', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('full_name', 'school', 'phone', 'is_approved')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('추가 정보', {'fields': ('full_name', 'school', 'phone')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
