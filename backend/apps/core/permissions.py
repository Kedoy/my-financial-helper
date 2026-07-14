"""
Custom permissions for the API.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение только для владельца объекта или read-only для остальных.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class IsOwner(permissions.BasePermission):
    """
    Разрешение только для владельца объекта.
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class IsProfileOwner(permissions.BasePermission):
    """
    Разрешение только для владельца профиля.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
