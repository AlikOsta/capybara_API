from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, Prefetch
from .models import Product, ProductView, Favorite
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer
)
from .permissions import IsAuthorOrReadOnly

class ProductViewSet(viewsets.ModelViewSet):
    """
    GET    /products/v1/products/             — список (только status=3, + свои для авториз.)
    POST   /products/v1/products/             — создать новое объявление
    GET    /products/v1/products/{pk}/        — детали + сохраняем просмотр
    PUT    /products/v1/products/{pk}/        — полный апдейт (только автор)
    PATCH  /products/v1/products/{pk}/        — частичный апдейт (только автор)
    DELETE /products/v1/products/{pk}/        — удалить (только автор)

    GET    /products/v1/products/favorites/   — список избранного текущего пользователя
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):

        qs = Product.objects.select_related(
                'author', 'category', 'currency', 'country', 'city'
            ).prefetch_related('images')\
             .annotate(
                views_count=Count('views', distinct=True),
                favorites_count=Count('favorited_by', distinct=True)
             )

        user = self.request.user

        if user.is_authenticated:
            
            qs = qs.prefetch_related(
                Prefetch(
                    'favorited_by',
                    queryset=Favorite.objects.filter(user=user),
                    to_attr='my_favorites'
                )
            )
            # показываем все опубликованные + свои черновики и архивы
            return qs.filter(Q(status=3) | Q(author=user))
        # анонимным — только опубликованные
        return qs.filter(status=3)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        if self.action == 'list' or self.action == 'favorites':
            return ProductListSerializer
        return ProductDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        # сохраняем просмотр
        instance = self.get_object()
        if request.user.is_authenticated:
            ProductView.objects.get_or_create(product=instance, user=request.user)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='favorites')
    def favorites(self, request):
        """
        Список избранного текущего пользователя
        """
        user = request.user
        qs = Product.objects.filter(favorited_by__user=user)\
            .select_related('author', 'category', 'currency', 'country', 'city')\
            .prefetch_related('images')\
            .annotate(
                views_count=Count('views', distinct=True),
                favorites_count=Count('favorited_by', distinct=True)
            )\
            .prefetch_related(
                Prefetch(
                    'favorited_by',
                    queryset=Favorite.objects.filter(user=user),
                    to_attr='my_favorites'
                )
            )

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


