from django.contrib.auth.views import (LogoutView, PasswordChangeDoneView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView)
from django.urls import path, reverse_lazy

from . import views
from .views import CustomPasswordResetView

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('register-success/', views.RegisterUserSuccess.as_view(), name='register_success'),
    path('password-change/', views.UserPasswordChange.as_view(), name='password_change'),
    path('password-change/done/',
        PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
        name='password_change_done'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/',
        PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
        name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                         success_url=reverse_lazy('users:password_reset_complete')),
        name='password_reset_confirm'),
    path('password_reset/complete/',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    path('profile/', views.UserProfile.as_view(), name='profile'),
]