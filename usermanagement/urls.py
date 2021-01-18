from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginUserView.as_view(), name='login_form'),
    path('logout/', LogoutUser.as_view(), name='logout_user')
]
