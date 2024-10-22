from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('register-success/', views.RegisterUserSuccess.as_view(), name='register_success'),
    path('profile/', views.UserProfile.as_view(), name='profile'),
]