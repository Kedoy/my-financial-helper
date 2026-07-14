from django.contrib import admin
from apps.categories.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'is_system', 'created_at']
    list_filter = ['type', 'is_system']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
