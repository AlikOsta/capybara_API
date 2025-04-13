from rest_framework import viewsets
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny
from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Category
from .serializers import CategorySerializer, CategoryDetailSerializer
from capybara_products.models import Product

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для работы с категориями продуктов.
    
    Предоставляет доступ только для чтения к списку категорий и детальной информации
    о конкретной категории, включая список опубликованных продуктов в ней.
    """
    
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    queryset = Category.objects.all().prefetch_related(
        Prefetch(
            'products',
            queryset=Product.objects.filter(status=3)
                .select_related('currency', 'country', 'city')
                .prefetch_related('images')
            
        )
    )

    @swagger_auto_schema(
        operation_summary="Получить список категорий",
        operation_description="Возвращает список всех категорий с базовой информацией",
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=CategorySerializer(many=True)
            ),
        },
        tags=['Categories']
    )
    def list(self, request, *args, **kwargs):
        """
        Получить список всех категорий.
        
        Возвращает список всех категорий с их основными атрибутами и количеством
        опубликованных продуктов в каждой категории.
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить детальную информацию о категории",
        operation_description="Возвращает детальную информацию о категории и список продуктов в ней",
        manual_parameters=[
            openapi.Parameter(
                name='slug',
                in_=openapi.IN_PATH,
                description='Уникальный идентификатор категории (slug)',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=CategoryDetailSerializer()
            ),
            404: "Категория не найдена"
        },
        tags=['Categories']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Получить детальную информацию о категории по её slug.
        
        Возвращает информацию о категории и список опубликованных продуктов,
        относящихся к этой категории.
        """
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от действия.
        
        Для детального представления используется CategoryDetailSerializer,
        для списка - CategorySerializer.
        """
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategorySerializer
