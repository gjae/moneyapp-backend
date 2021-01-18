from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse
from .forms import LoginForm


class LoginUserView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


class LogoutUser(LogoutView):
    template_name = 'logout.html'
    next_page = '/login/'
    redirect_field_name = 'next_page'