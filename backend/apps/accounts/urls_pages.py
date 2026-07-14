from django.urls import path
from . import views_pages

app_name = 'auth_pages'

urlpatterns = [
    path('login/', views_pages.login_view, name='login'),
    path('register/', views_pages.register_view, name='register'),
    path('logout/', views_pages.logout_view, name='logout'),
    path('profile/', views_pages.profile_view, name='profile'),
]
