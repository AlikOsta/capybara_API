
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import TelegramUser, UserRating
from .serializers import (
    TelegramUserSerializer, 
    UserRatingSerializer, 
    UserRatingCreateUpdateSerializer
)

from .permissions import IsSelfOrReadOnly, IsRatingAuthorOrReadOnly

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
    
    @swagger_auto_schema(
        method='get',
        operation_summary="Получить рейтинг пользователя",
        operation_description="Возвращает средний рейтинг пользователя и количество оценок",
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'average_rating': openapi.Schema(type=openapi.TYPE_NUMBER, description='Средний рейтинг пользователя'),
                        'ratings_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Количество оценок')
                    }
                )
            ),
            404: "Пользователь не найден"
        },
        tags=['Users']
    )
    @action(detail=True, methods=['get'])
    def rating(self, request, pk=None):
        """
        Получить рейтинг пользователя.
        
        Возвращает средний рейтинг пользователя и количество полученных оценок.
        """
        user = self.get_object()
        return Response({
            'average_rating': user.average_rating,
            'ratings_count': user.ratings_count
        })
    
    @swagger_auto_schema(
        method='get',
        operation_summary="Получить оценки, оставленные текущим пользователем",
        operation_description="Возвращает список оценок, которые текущий пользователь оставил другим пользователям",
        responses={
            200: UserRatingSerializer(many=True),
            401: "Не авторизован"
        },
        tags=['Users']
    )
    @action(detail=False, methods=['get'])
    def my_ratings(self, request):
        """
        Получить оценки, оставленные текущим пользователем.
        
        Требуется авторизация. Возвращает список оценок, которые текущий пользователь оставил другим пользователям.
        """
        ratings = UserRating.objects.filter(from_user=request.user).select_related('to_user')
        serializer = UserRatingSerializer(ratings, many=True, context={'request': request})
        return Response(serializer.data)
    

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
    
    @swagger_auto_schema(
        operation_summary="Получить список оценок пользователя",
        operation_description="Возвращает список оценок, полученных конкретным пользователем",
        responses={
            200: UserRatingSerializer(many=True),
            404: "Пользователь не найден"
        },
        tags=['Ratings']
    )
    def list(self, request, *args, **kwargs):
        """
        Получить список оценок пользователя.
        """
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Оценить пользователя",
        operation_description="Создает новую оценку для пользователя. Один пользователь может оставить только одну оценку другому пользователю.",
        request_body=UserRatingCreateUpdateSerializer,
        responses={
            201: UserRatingSerializer(),
            400: "Неверные данные или вы уже оценили этого пользователя",
            401: "Не авторизован",
            404: "Пользователь не найден"
        },
        tags=['Ratings']
    )
    def create(self, request, *args, **kwargs):
        """
        Оценить пользователя.
        
        Требуется авторизация. Один пользователь может оставить только одну оценку другому пользователю.
        Пользователь не может оценить сам себя.
        """
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Получить оценку",
        operation_description="Возвращает детальную информацию о конкретной оценке",
        responses={
            200: UserRatingSerializer(),
            404: "Оценка не найдена"
        },
        tags=['Ratings']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Получить детальную информацию об оценке.
        """
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Обновить оценку (полное обновление)",
        operation_description="Полностью обновляет оценку. Доступно только автору оценки.",
        request_body=UserRatingCreateUpdateSerializer,
        responses={
            200: UserRatingSerializer(),
            400: "Неверные данные",
            401: "Не авторизован",
            403: "Доступ запрещен",
            404: "Оценка не найдена"
        },
        tags=['Ratings']
    )
    def update(self, request, *args, **kwargs):
        """
        Обновить оценку (полное обновление).
        
        Требуется авторизация. Доступно только автору оценки.
        """
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Обновить оценку (частичное обновление)",
        operation_description="Частично обновляет оценку. Доступно только автору оценки.",
        request_body=UserRatingCreateUpdateSerializer,
        responses={
            200: UserRatingSerializer(),
            400: "Неверные данные",
            401: "Не авторизован",
            403: "Доступ запрещен",
            404: "Оценка не найдена"
        },
        tags=['Ratings']
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Обновить оценку (частичное обновление).
        
        Требуется авторизация. Доступно только автору оценки.
        """
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Удалить оценку",
        operation_description="Удаляет оценку. Доступно только автору оценки.",
        responses={
            204: "Оценка успешно удалена",
            401: "Не авторизован",
            403: "Доступ запрещен",
            404: "Оценка не найдена"
        },
        tags=['Ratings']
    )
    def destroy(self, request, *args, **kwargs):
        """
        Удалить оценку.
        
        Требуется авторизация. Доступно только автору оценки.
        """
        return super().destroy(request, *args, **kwargs)
