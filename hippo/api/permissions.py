from rest_framework import permissions


class JobPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.method in permissions.SAFE_METHODS and obj.public
