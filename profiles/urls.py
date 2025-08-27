from django.urls import path
from .views import signup_view, CustomLoginView, approve_users_view, approve_user_action
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', CustomLoginView.as_view(template_name='profiles/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('admin/approve/', approve_users_view, name='approve_users'),
    path('admin/approve/<int:user_id>/', approve_user_action, name='approve_user'),
    path('admin/approve/', approve_users_view, name='approve_users'),
    path('admin/approve/<int:user_id>/', approve_user_action, name='approve_user'),

]
