
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import TelegramUser, UserRating
from .serializers import (TelegramUserSerializer, 
    UserRatingSerializer, UserRatingCreateUpdateSerializer)

from .permissions import IsSelfOrReadOnly, IsRatingAuthorOrReadOnly

class UserViewSet(viewsets.ModelViewSet):
    """
    API для работы с пользователями Telegram.
    
    Предоставляет доступ к списку пользователей, детальной информации о пользователе,
    а также возможность обновления данных пользователя (только для самого пользователя).
    """
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrReadOnly]

    # def list(self, request, *args, **kwargs):
    #     """
    #     Получить список всех пользователей.
        
    #     Требуется авторизация. Возвращает список всех пользователей Telegram
    #     с их основными данными и списком созданных ими продуктов.
    #     """
    #     return super().list(request, *args, **kwargs)

    # def retrieve(self, request, *args, **kwargs):
    #     """
    #     Получить детальную информацию о пользователе по его идентификатору.
        
    #     Требуется авторизация. Возвращает информацию о конкретном пользователе,
    #     включая его профиль и список созданных им продуктов.
    #     """
    #     return super().retrieve(request, *args, **kwargs)

    # def update(self, request, *args, **kwargs):
    #     """
    #     Полностью обновить данные пользователя.
        
    #     Требуется авторизация. Пользователь может обновлять только свои собственные данные.
    #     Поля id, username и telegram_id не могут быть изменены.
    #     """
    #     return super().update(request, *args, **kwargs)

    # def partial_update(self, request, *args, **kwargs):
    #     """
    #     Частично обновить данные пользователя.
        
    #     Требуется авторизация. Пользователь может обновлять только свои собственные данные.
    #     Можно обновить одно или несколько полей. Поля id, username и telegram_id не могут быть изменены.
    #     """
    #     return super().partial_update(request, *args, **kwargs)
    
    # @action(detail=True, methods=['get'])
    # def rating(self, request, pk=None):
    #     """
    #     Получить рейтинг пользователя.
        
    #     Возвращает средний рейтинг пользователя и количество полученных оценок.
    #     """
    #     user = self.get_object()
    #     return Response({
    #         'average_rating': user.average_rating,
    #         'ratings_count': user.ratings_count
    #     })
    
    # @action(detail=False, methods=['get'])
    # def my_ratings(self, request):
    #     """
    #     Получить оценки, оставленные текущим пользователем.
        
    #     Требуется авторизация. Возвращает список оценок, которые текущий пользователь оставил другим пользователям.
    #     """
    #     ratings = UserRating.objects.filter(from_user=request.user).select_related('to_user')
    #     serializer = UserRatingSerializer(ratings, many=True, context={'request': request})
    #     return Response(serializer.data)
    

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
    
    def list(self, request, *args, **kwargs):
        """
        Получить список оценок пользователя.
        """
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """
        Оценить пользователя.
        
        Требуется авторизация. Один пользователь может оставить только одну оценку другому пользователю.
        Пользователь не может оценить сам себя.
        """
        return super().create(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Получить детальную информацию об оценке.
        """
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Обновить оценку (полное обновление).
        
        Требуется авторизация. Доступно только автору оценки.
        """
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Обновить оценку (частичное обновление).
        
        Требуется авторизация. Доступно только автору оценки.
        """
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Удалить оценку.
        
        Требуется авторизация. Доступно только автору оценки.
        """
        return super().destroy(request, *args, **kwargs)
