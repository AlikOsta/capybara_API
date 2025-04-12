from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Позволяет менять/удалять/апдейтить объект только его автору.
    Все SAFE_METHODS — разрешены всем.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
