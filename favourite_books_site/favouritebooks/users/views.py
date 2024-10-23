from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from books.utils import DataMixin
from favouritebooks import settings
from users.forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm, \
    CustomPasswordResetForm


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    page_title = 'Login'

class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    page_title = 'Register'
    success_url = reverse_lazy('users:register_success')

class RegisterUserSuccess(DataMixin, TemplateView):
    template_name = 'users/register_success.html'
    page_title = 'Success'

class UserProfile(LoginRequiredMixin, DataMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    page_title = 'User Profile'

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

class UserPasswordChange(DataMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change.html'
    page_title = 'Password change'


class CustomPasswordResetView(PasswordResetView):
     form_class = CustomPasswordResetForm
     template_name = 'users/password_reset.html'
     email_template_name = 'users/password_reset_email.html'
     success_url = reverse_lazy('users:password_reset_done')
