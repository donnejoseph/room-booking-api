from rest_framework import permissions
from typing import Any, Optional


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow admin users to create, update, or delete objects.
    Regular users can only view.
    """
    
    def has_permission(self, request, view) -> bool:
        # Allow GET, HEAD and OPTIONS requests for any user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admin users
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of an object or admins to view or edit it.
    """
    
    def has_object_permission(self, request, view, obj) -> bool:
        # Check if user is admin
        if request.user and request.user.is_staff:
            return True
        
        # Check if obj has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        return False 