from .views.view_users import *
from .views.view_game import *
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Tic Tac Toe API",
      default_version='v1',
      description="API documentation for Tic Tac Toe game",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="mtqn0310@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
   path('api/login/', login_user, name='login_user'),
   path('api/logout/', logout_user, name='logout_user'),
   path('api/register/', register_user, name='register_user'),
   path('api/verifyemail/', verifyemail, name='verify_email'),
   path('api/get_user/', get_user, name='get_user'),
   
   path('api/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
   path('api/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
   path('api/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
   path('api/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('api/game/', tictactoe_game, name='tictactoe_game'),
    path('api/make_move/', make_move, name='make_move'),
    path('api/new_game/', reset_game, name='reset_game'),
    path('api/tictactoe_result/', tictactoe_result, name='tictactoe_result'),
    path('api/history/', game_history, name='game_history'),
    path('api/get_moves/', game_moves, name='game_moves'),
    path('api/update_account/', update_profile, name='update_profile'),
    path('api/resend_email/', verifyemail_resend, name='verifyemail_resend'),
    path('api/game_log/', get_game_log, name='game_log'),
    
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]