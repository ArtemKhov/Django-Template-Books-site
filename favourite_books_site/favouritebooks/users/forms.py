from django import forms

class LoginUserForm(forms.Form):
    username = forms.CharField(label='Login')
    password = forms.CharField(label='Password')