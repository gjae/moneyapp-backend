from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UsernameField

class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'Combinacion de usuario y contraseña invalida',
        'test': 'SI'
    }