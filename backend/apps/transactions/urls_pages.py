from django.urls import path
from . import views_pages

app_name = 'transactions'

urlpatterns = [
    path('', views_pages.transaction_list, name='list'),
    path('create/', views_pages.transaction_create, name='create'),
    path('<int:pk>/edit/', views_pages.transaction_edit, name='edit'),
    path('<int:pk>/delete/', views_pages.transaction_delete, name='delete'),
    path('sms-parse/', views_pages.sms_parse_view, name='sms_parse'),
    path('sms-confirm/', views_pages.sms_confirm, name='sms_confirm'),
]
