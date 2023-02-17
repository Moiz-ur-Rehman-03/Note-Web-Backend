from rest_framework import permissions


class IsSharedWith(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        allowed_methods = ('GET', 'PUT', 'PATCH')

        user = request.user
        shared_with = obj.shared_with.all()

        if request.method in allowed_methods:
            return True

        if user.id in shared_with:
            return True

        return False


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        allowed_methods = ('POST', 'GET', 'PUT', 'PATCH', 'DELETE')

        if request.method in allowed_methods:
            return True

        if user == obj.author:
            return True

        return False
