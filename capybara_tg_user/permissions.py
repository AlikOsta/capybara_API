
from rest_framework import permissions

class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Позволяет менять только свой собственный объект (user.pk == request.user.pk).
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.pk == request.user.pk
    

class IsRatingAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее пользователям редактировать только свои оценки.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.from_user == request.user
