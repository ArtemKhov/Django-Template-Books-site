from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Login')
    password = forms.CharField(label='Password')

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']