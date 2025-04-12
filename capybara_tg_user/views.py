# views.py
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .models import TelegramUser
from .serializers import TelegramUserSerializer
from .permissions import IsSelfOrReadOnly

class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, viewsets.GenericViewSet ):
    """
    GET /users/v1/users/ - список всех пользователей

    GET /users/v1/users/{pk}/ - конкретный пользователь

    PUT /users/v1/users/{pk}/ - Изментить данный пользователя

    PATCH /users/v1/users/{pk}/ - 
    """
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrReadOnly]

