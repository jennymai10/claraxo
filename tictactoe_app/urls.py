from django.urls import path
from .views.view_users import *
from .views.view_game import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', login_user, name='login_user'),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    
    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    path('register/', register_user, name='register_user'),
    path('verify_email/', verify_email, name='verify_email'),
    path('users/', get_users, name='get_users'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('game/', tictactoe_game, name='tictactoe_game'),
    path('make_move/', make_move, name='make_move'),
    path('new_game/', reset_game, name='reset_game'),
    path('tictactoe_result/', tictactoe_result, name='tictactoe_result'),
    path('history/', game_history, name='game_history'),
    path('get_user_type/',get_user_type,name='get_user_type/'),
    path('get_moves/',get_game_moves,name='get_moves/'),
]