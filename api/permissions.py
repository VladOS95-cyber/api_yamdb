from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.role in ('moderator', 'admin'):
            return True
        return obj.author == request.user


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if (request.user.role == 'admin'
                or request.user.is_superuser is True):
            return True


class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.role == 'admin'
                or request.user.role == 'moderator')


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (True if request.method in permissions.SAFE_METHODS
                else request.user.is_authenticated
                and (request.user.is_staff or request.user.role == 'admin'))
