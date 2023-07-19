from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class OwnerOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        print(request.method)
        return request.method == 'POST'

    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.user is permissions.IsAdminUser
        )