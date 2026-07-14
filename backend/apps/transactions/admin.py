from django.contrib import admin
from apps.transactions.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'type', 'category', 'source', 'date']
    list_filter = ['type', 'source', 'is_ai_parsed', 'date']
    search_fields = ['description', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')
