
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Prefetch

from .models import Product, ProductView, Favorite
from .serializers import (
    ProductListSerializer, 
    ProductDetailSerializer, 
    ProductCreateUpdateSerializer,   
)
from .permissions import IsAuthorOrReadOnly, IsCommentAuthorOrReadOnly
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
    
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.get_base_queryset().filter(favorited_by__user=user)
        return self.add_favorites_prefetch(queryset, user)
    
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


