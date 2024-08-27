from django.urls import path

from .views import register_user
from . import views
from .views import handle_login

urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('users/', views.get_users, name='get_users'),
    path('login/', handle_login, name='login'),
]