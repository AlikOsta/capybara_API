
import json
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from urllib.parse import parse_qs
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from .models import TelegramUser, UserRating
from .serializers import (TelegramUserSerializer, 
    UserRatingSerializer, UserRatingCreateUpdateSerializer)

from .permissions import IsSelfOrReadOnly, IsRatingAuthorOrReadOnly
from .verify_telegram import verify_telegram_init_data


logger = logging.getLogger(__name__)


class TelegramAuthView(APIView):
    """
    API для регистрации пользователя.

    Аутентификация через Telegram Mini App.
    Получает initData от фронтенда, проверяет его и выдаёт JWT-токены.
    """
    def post(self, request):
        init_data = request.data.get('initData')
        if not init_data:
            return Response({'error': 'No initData provided'}, status=status.HTTP_400_BAD_REQUEST)
        # 1
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not verify_telegram_init_data(init_data, bot_token):
            return Response({"detail": "Invalid init_data"}, status=status.HTTP_403_FORBIDDEN)

        # 2
        params = parse_qs(init_data, keep_blank_values=True)
        params = {k: v[0] for k, v in params.items()}
        user_json = params.get('user')
        if not user_json:
            return Response({"detail": "No user data provided"}, status=status.HTTP_400_BAD_REQUEST)
        user_data = json.loads(user_json)

        tg_id = user_data.get('id')
        if not tg_id:
            return Response({"detail": "No Telegram ID provided"}, status=status.HTTP_400_BAD_REQUEST)
        # 3
        user, created = TelegramUser.objects.get_or_create(telegram_id=tg_id, defaults={
            "username": user_data.get('username') or f"tg_{tg_id}",
            "first_name": user_data.get('first_name', ''),
            "last_name": user_data.get('last_name', ''),
            "language": user_data.get('language_code', ''),
        })
        if not created:
            # При повторном входе можно обновить имя/юзернейм на случай изменений в Telegram
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name  = user_data.get('last_name', user.last_name)
            uname = user_data.get('username')
            user.language = user_data.get('language_code', '')

            if uname:
                user.username = uname
            user.save()

        # 4 
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # 5
        response = Response({"detail": "Authentication successful"}
                           , status=status.HTTP_200_OK)
        cookie_max_age = 3600 * 24 * 7
        response.set_cookie(
            key='access_token', value=access_token,
            max_age=60*15, httponly=True, secure=True, samesite='Strict'
        )
        response.set_cookie(
            key='refresh_token', value=refresh_token,
            max_age=cookie_max_age, httponly=True, secure=True, samesite='Strict'
        )
        return response
    

class TokenRefreshFromCookieView(APIView):
    """
    API для Обновление access-токена через refresh-токен.

    Обновление access-токена через refresh-токен в HttpOnly cookie.
    """
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"detail": "Refresh token missing"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            refresh = RefreshToken(refresh_token)
        except TokenError:
            logger.error("Invalid refresh token")
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        new_access = str(refresh.access_token)
        response = Response({"detail": "Access token refreshed"})
        # Обновляем куку access_token
        response.set_cookie(
            key='access_token', value=new_access,
            max_age=60*15, httponly=True, secure=True, samesite='Strict'
        )
        return response



class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    API для работы с пользователями Telegram.
    
    Предоставляет доступ к списку пользователей, детальной информации о пользователе,
    а также возможность обновления данных пользователя (только для самого пользователя).
    """
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrReadOnly]


class UserRatingViewSet(viewsets.ModelViewSet):
    """
    API для работы с рейтингами пользователей.
    
    Предоставляет возможность получать, создавать, обновлять и удалять рейтинги пользователей.
    Один пользователь может оставить только одну оценку другому пользователю.
    """
    permission_classes = [IsAuthenticated, IsRatingAuthorOrReadOnly]
    
    def get_queryset(self):
        """
        Возвращает рейтинги для конкретного пользователя.
        """
        to_user_id = self.kwargs.get('user_pk')
        return UserRating.objects.filter(to_user_id=to_user_id).select_related('from_user')
    
    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от действия.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return UserRatingCreateUpdateSerializer
        return UserRatingSerializer
    
    def get_serializer_context(self):
        """
        Добавляет ID оцениваемого пользователя в контекст сериализатора.
        """
        context = super().get_serializer_context()
        context['to_user_id'] = self.kwargs.get('user_pk')
        return context
    
    def perform_create(self, serializer):
        """
        Создает новую оценку, связывая ее с текущим пользователем и оцениваемым пользователем.
        """
        to_user_id = self.kwargs.get('user_pk')
        serializer.save(from_user=self.request.user, to_user_id=to_user_id)
    

