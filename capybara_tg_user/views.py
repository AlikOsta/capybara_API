
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import TelegramUser
from .serializers import TelegramUserSerializer
from .permissions import IsSelfOrReadOnly

class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    API для работы с пользователями Telegram.
    
    Предоставляет доступ к списку пользователей, детальной информации о пользователе,
    а также возможность обновления данных пользователя (только для самого пользователя).
    """
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Получить список пользователей",
        operation_description="Возвращает список всех пользователей Telegram, зарегистрированных в системе",
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=TelegramUserSerializer(many=True)
            ),
            401: "Не авторизован"
        },
        tags=['Users']
    )
    def list(self, request, *args, **kwargs):
        """
        Получить список всех пользователей.
        
        Требуется авторизация. Возвращает список всех пользователей Telegram
        с их основными данными и списком созданных ими продуктов.
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить информацию о пользователе",
        operation_description="Возвращает детальную информацию о конкретном пользователе по его идентификатору",
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                description='Уникальный идентификатор пользователя',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=TelegramUserSerializer()
            ),
            401: "Не авторизован",
            404: "Пользователь не найден"
        },
        tags=['Users']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Получить детальную информацию о пользователе по его идентификатору.
        
        Требуется авторизация. Возвращает информацию о конкретном пользователе,
        включая его профиль и список созданных им продуктов.
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновить данные пользователя (полное обновление)",
        operation_description="Полностью обновляет данные пользователя. Доступно только самому пользователю.",
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                description='Уникальный идентификатор пользователя',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['first_name', 'last_name', 'photo_url'],
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Фамилия пользователя'),
                'photo_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL фотографии пользователя'),
            }
        ),
        responses={
            200: TelegramUserSerializer(),
            400: "Неверные данные",
            401: "Не авторизован",
            403: "Доступ запрещен",
            404: "Пользователь не найден"
        },
        tags=['Users']
    )
    def update(self, request, *args, **kwargs):
        """
        Полностью обновить данные пользователя.
        
        Требуется авторизация. Пользователь может обновлять только свои собственные данные.
        Поля id, username и telegram_id не могут быть изменены.
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновить данные пользователя (частичное обновление)",
        operation_description="Частично обновляет данные пользователя. Доступно только самому пользователю.",
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                description='Уникальный идентификатор пользователя',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Фамилия пользователя'),
                'photo_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL фотографии пользователя'),
            }
        ),
        responses={
            200: TelegramUserSerializer(),
            400: "Неверные данные",
            401: "Не авторизован",
            403: "Доступ запрещен",
            404: "Пользователь не найден"
        },
        tags=['Users']
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Частично обновить данные пользователя.
        
        Требуется авторизация. Пользователь может обновлять только свои собственные данные.
        Можно обновить одно или несколько полей. Поля id, username и telegram_id не могут быть изменены.
        """
        return super().partial_update(request, *args, **kwargs)
