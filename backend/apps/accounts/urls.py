from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    CustomTokenRefreshView,
    ProfileView,
    ProfileDetailView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('me/', ProfileView.as_view(), name='profile-me'),
    path('profile/', ProfileDetailView.as_view(), name='profile-detail'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
