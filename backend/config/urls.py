from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts.views_pages import dashboard_view

# Swagger/OpenAPI documentation
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Страницы
    path('', dashboard_view, name='dashboard'),
    path('auth/', include('apps.accounts.urls_pages')),
    path('transactions/', include('apps.transactions.urls_pages')),

    # API v1 endpoints
    path('api/v1/', include('apps.core.urls')),  # Health checks (must be first)
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/transactions/', include('apps.transactions.urls')),
    path('api/v1/categories/', include('apps.categories.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/blog/', include('apps.blog.urls')),

    # Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = 'Ks Financial App Admin'
admin.site.site_title = 'Ks Financial App Admin Portal'
admin.site.index_title = 'Welcome to Ks Financial App Admin Portal'
