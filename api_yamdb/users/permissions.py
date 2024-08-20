from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsAdminOrSelf(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        else:
            return request.user.is_admin

    def has_object_permission(self, request, view, obj):
        if request.method in ['PATCH', 'PUT', 'DELETE']:
            return request.user.is_authenticated and (request.user.is_admin or request.user == obj.author)
        return True
