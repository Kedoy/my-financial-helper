from django.urls import path
from .views_health import health_check, readiness_check

app_name = 'core'

urlpatterns = [
    # Health checks at api/v1/ level
    path('health/', health_check, name='health'),
    path('ready/', readiness_check, name='readiness'),
]
