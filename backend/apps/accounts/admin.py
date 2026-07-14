from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('phone',)}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('email', 'phone')}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'currency', 'created_at']
    list_filter = ['currency']
    search_fields = ['user__email', 'bio']
    readonly_fields = ['created_at', 'updated_at']
