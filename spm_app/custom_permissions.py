from rest_framework import permissions
from django.db.models import Q


class AccessPermissions(permissions.BasePermission):
    """
    Custom permission to only allow authenticated to access api
    """

    def has_permission(self, request, view):
        """
        Handles permissions for the entire API.
        By default:
            - only allow:
                - authenticated
        """
        return request.user.is_authenticated


class AdminGroupOnlyPermissions(permissions.BasePermission):
    """
    Custom permission to only allow authenticated to access api
    """

    def has_permission(self, request, view):
        """
        Handles permissions for the entire API.
        By default:
            - only allow:
                - authenticated administrators
        """
        return request.user.groups.filter(
            name='administrators').exists()


class CustomPermissionsCheck:

    def is_administrator(user=None):
        """
        pass (return True) if user is:
            - in administrators group or is a superuser
        """
        if user:
            return user.groups.filter(
                name='administrators').exists() or user.is_superuser
        return False
