from django.urls import path
from .views import register_user, change_username
from . import views

urlpatterns = [
    path('', register_user, name='register_user'),
    path('register/', register_user, name='register_user'),
    path('users/', views.get_users, name='get_users'),
    path('manage_account/', views.manage_account, name='manage_account'),
    path('change-username/', views.change_username, name='change_username'),
    path('change-email/', views.change_email, name='change_email'),
    path('change-date-of-birth/', views.change_date_of_birth, name='change_date_of_birth'),
    path('change-password/', views.change_password, name='change_password'),
]