from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.transactions.views import TransactionViewSet

# Router для транзакций
router = DefaultRouter()
router.register(r'', TransactionViewSet, basename='transaction')

urlpatterns = router.urls
