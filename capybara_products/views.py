from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Prefetch

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Product, ProductView, Favorite
from .serializers import (
    ProductListSerializer, 
    ProductDetailSerializer, 
    ProductCreateUpdateSerializer
)
from .permissions import IsAuthorOrReadOnly
from .filters import ProductFilterSet

class ProductQuerySetMixin:
    """Миксин для общей логики формирования QuerySet продуктов"""
    
    def get_base_queryset(self):
        """Базовый QuerySet с предзагрузкой связанных объектов и аннотациями"""
        return Product.objects.select_related(
            'author', 'category', 'currency', 'country', 'city'
        ).prefetch_related('images')\
         .annotate(
            views_count=Count('views', distinct=True),
            favorites_count=Count('favorited_by', distinct=True)
         )
    
    def add_favorites_prefetch(self, queryset, user):
        """Добавляет prefetch для избранных продуктов пользователя"""
        if not user.is_authenticated:
            return queryset
            
        return queryset.prefetch_related(
            Prefetch(
                'favorited_by',
                queryset=Favorite.objects.filter(user=user),
                to_attr='my_favorites'
            )
        )


class ProductViewSet(ProductQuerySetMixin, viewsets.ModelViewSet):
    """
    API для работы с продуктами (объявлениями).
    
    Предоставляет полный набор CRUD-операций для продуктов, а также
    дополнительные действия для управления избранными продуктами.
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filterset_class = ProductFilterSet
    search_fields = ['title', 'description']
    ordering_fields = ['create_at', 'price', 'views_count', 'favorites_count']
    ordering = ['-create_at']

    @swagger_auto_schema(
        operation_summary="Получить список продуктов",
        operation_description="Возвращает список продуктов с возможностью фильтрации, поиска и сортировки",
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Поиск по названию и описанию",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY,
                description="Сортировка: create_at, -create_at, price, -price, views_count, favorites_count",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'category', openapi.IN_QUERY,
                description="Фильтр по ID категории",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'country', openapi.IN_QUERY,
                description="Фильтр по ID страны (работает только если указана категория)",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'city', openapi.IN_QUERY,
                description="Фильтр по ID города (работает только если указана категория)",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'currency', openapi.IN_QUERY,
                description="Фильтр по ID валюты (работает только если указана категория)",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=ProductListSerializer(many=True)
            ),
        },
        tags=['Products']
    )
    def list(self, request, *args, **kwargs):
        """
        Получить список продуктов.
        
        Для неавторизованных пользователей возвращает только опубликованные продукты (status=3).
        Для авторизованных пользователей также включает их собственные продукты независимо от статуса.
        
        Поддерживает:
        - Поиск по названию и описанию
        - Сортировку по дате создания, цене, количеству просмотров и избранных
        - Фильтрацию по категории, стране, городу и валюте (фильтры кроме категории работают только если указана категория)
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создать новый продукт",
        operation_description="Создает новый продукт. Требуется авторизация.",
        request_body=ProductCreateUpdateSerializer,
        responses={
            201: openapi.Response(
                description="Продукт успешно создан",
                schema=ProductDetailSerializer()
            ),
            400: "Неверные данные",
            401: "Не авторизован"
        },
        tags=['Products']
    )
    def create(self, request, *args, **kwargs):
        """
        Создать новый продукт.
        
        Требуется авторизация. Текущий пользователь автоматически устанавливается как автор продукта.
        Поддерживает загрузку одного изображения.
        """
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить детальную информацию о продукте",
        operation_description="Возвращает детальную информацию о продукте по его ID. При просмотре авторизованным пользователем сохраняется запись о просмотре.",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH,
                description="ID продукта",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=ProductDetailSerializer()
            ),
            404: "Продукт не найден"
        },
        tags=['Products']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Получить детальную информацию о продукте.
        
        Возвращает полную информацию о продукте, включая данные о стране, городе, авторе и т.д.
        Если пользователь авторизован, при просмотре продукта создается запись о просмотре.
        """
        instance = self.get_object()
        if request.user.is_authenticated:
            ProductView.objects.get_or_create(product=instance, user=request.user)
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновить продукт (полное обновление)",
        operation_description="Полностью обновляет продукт. Доступно только автору продукта.",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH,
                description="ID продукта",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=ProductCreateUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Продукт успешно обновлен",
                schema=ProductDetailSerializer()
            ),
            400: "Неверные данные",
            401: "Не авторизован",
            403: "Доступ запрещен",
            404: "Продукт не найден"
        },
        tags=['Products']
    )
    def update(self, request, *args, **kwargs):
        """
        Обновить продукт (полное обновление).
        
        Требуется авторизация. Доступно только автору продукта.
        Все поля должны быть предоставлены в запросе.
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновить продукт (частичное обновление)",
        operation_description="Частично обновляет продукт. Доступно только автору продукта.",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH,
                description="ID продукта",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=ProductCreateUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Продукт успешно обновлен",
                schema=ProductDetailSerializer()
            ),
            400: "Неверные данные",
            401: "Не авторизован",
            403: "Доступ запрещен",
            404: "Продукт не найден"
        },
        tags=['Products']
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Обновить продукт (частичное обновление).
        
        Требуется авторизация. Доступно только автору продукта.
        Можно предоставить только те поля, которые нужно обновить.
        """
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удалить продукт",
        operation_description="Удаляет продукт. Доступно только автору продукта.",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH,
                description="ID продукта",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            204: "Продукт успешно удален",
            401: "Не авторизован",
            403: "Доступ запрещен",
            404: "Продукт не найден"
        },
        tags=['Products']
    )
    def destroy(self, request, *args, **kwargs):
        """
        Удалить продукт.
        
        Требуется авторизация. Доступно только автору продукта.
        """
        return super().destroy(request, *args, **kwargs)

    def get_filter_backends(self):
        backends = [SearchFilter]
        if 'category' in self.request.query_params:
            backends += [DjangoFilterBackend, OrderingFilter]
        return backends

    def get_queryset(self):
        queryset = self.get_base_queryset()
        queryset = self.add_favorites_prefetch(queryset, self.request.user)
        
        user = self.request.user
        if user.is_authenticated:
            return queryset.filter(Q(status=3) | Q(author=user))
        return queryset.filter(status=3)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer


class FavoriteViewSet(ProductQuerySetMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API для работы с избранными продуктами.
    
    Позволяет получать список избранных продуктов, а также добавлять и удалять продукты из избранного.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProductListSerializer
    
    @swagger_auto_schema(
        operation_summary="Получить список избранных продуктов",
        operation_description="Возвращает список продуктов, добавленных в избранное текущим пользователем",
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=ProductListSerializer(many=True)
            ),
            401: "Не авторизован"
        },
        tags=['Favorites']
    )
    def list(self, request, *args, **kwargs):
        """
        Получить список избранных продуктов.
        
        Требуется авторизация. Возвращает список продуктов, добавленных в избранное текущим пользователем.
        """
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.get_base_queryset().filter(favorited_by__user=user)
        return self.add_favorites_prefetch(queryset, user)
    
    # Важно: декораторы swagger_auto_schema должны быть ПЕРЕД декоратором action
    @swagger_auto_schema(
        method='post',
        operation_summary="Добавить продукт в избранное",
        operation_description="Добавляет продукт в избранное текущего пользователя",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH,
                description="ID продукта",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'is_favorited': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Добавлен ли продукт в избранное'),
                        'favorites_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Общее количество добавлений продукта в избранное')
                    }
                )
            ),
            401: "Не авторизован",
            404: "Продукт не найден"
        },
        tags=['Favorites']
    )
    @swagger_auto_schema(
        method='delete',
        operation_summary="Удалить продукт из избранного",
        operation_description="Удаляет продукт из избранного текущего пользователя",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH,
                description="ID продукта",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'is_favorited': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Добавлен ли продукт в избранное'),
                        'favorites_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Общее количество добавлений продукта в избранное')
                    }
                )
            ),
            401: "Не авторизован",
            404: "Продукт не найден"
        },
        tags=['Favorites']
    )
    @action(detail=True, methods=['post', 'delete'])
    def toggle(self, request, pk=None):
        """
        Добавить/удалить объявление из избранного.
        
        Требуется авторизация.
        - POST: добавляет продукт в избранное
        - DELETE: удаляет продукт из избранного
        
        Возвращает:
        - is_favorited: добавлен ли продукт в избранное
        - favorites_count: общее количество добавлений продукта в избранное
        """
        try:
            product = Product.objects.get(pk=pk)
            user = request.user

            if request.method == 'POST':
                fav, created = Favorite.objects.get_or_create(user=user, product=product)
            else:
                deleted = Favorite.objects.filter(user=user, product=product).delete()[0] > 0
                created = False

            count = Product.objects.filter(pk=product.pk)\
                .annotate(favorites_count=Count('favorited_by', distinct=True))\
                .first().favorites_count

            return Response(
                {
                    "is_favorited": bool(created),
                    "favorites_count": count
                },
                status=status.HTTP_200_OK
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
