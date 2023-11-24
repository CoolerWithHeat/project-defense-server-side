from rest_framework.permissions import BasePermission

class DenyAnonymousPermission(BasePermission):
    def has_permission(self, request, *args, **kwargs):
        return not request.user.is_anonymous

class OnlyAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.admin