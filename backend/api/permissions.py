"""
IsAuthorOrRead - Если не автор, то только чтение. 
"""

from rest_framework import permissions


class IsAuthorOrRead(permissions.BasePermission):
    """Если не автор, то только чтение."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
