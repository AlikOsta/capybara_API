from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Prefetch

from .models import Product, ProductView, Favorite
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer
from .permissions import IsAuthorOrReadOnly


class ProductViewSet(viewsets.ModelViewSet):
    """
      • GET    /products/v1/products/             — список (только status=3 + свои для авториз.)
      • POST   /products/v1/products/             — создать объявление

      • GET    /products/v1/products/{pk}/        — детали + сохраняем просмотр
      • PUT    /products/v1/products/{pk}/        — полный апдейт (только автор)
      • PATCH  /products/v1/products/{pk}/        — частичный апдейт (только автор)
      • DELETE /products/v1/products/{pk}/        — удалить (только автор)

      • GET    /products/v1/products/favorites/   — список избранного
      • POST   /products/v1/products/{pk}/favorite/   — добавить в избранное
      • DELETE /products/v1/products/{pk}/favorite/   — убрать из избранного

    Параметры запроса:
      • search — регистронезависимый поиск по title и description
      • ordering — сортировка: create_at, -create_at, price, -price, views_count, favorites_count
      • фильтрация (только если указан ?category=…): country, city, currency, category
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    # DRF-фильтры
    filterset_fields = ['country', 'city', 'currency', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['create_at', 'price', 'views_count', 'favorites_count']
    ordering = ['-create_at']  

    def get_filter_backends(self):

        backends = [SearchFilter]

        if 'category' in self.request.query_params:
            backends += [DjangoFilterBackend, OrderingFilter]

        return backends

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

            return qs.filter(Q(status=3))

        return qs.filter(status=3)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        if self.action in ['list', 'favorites']:
            return ProductListSerializer
        return ProductDetailSerializer

    def perform_create(self, serializer):
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_authenticated:
            ProductView.objects.get_or_create(product=instance, user=request.user)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='favorites')
    def favorites(self, request):
        """
        Список избранных объявлений
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

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated], url_path='favorite')
    def favorite(self, request, pk=None):
        '''
        Добавить/удалить объявление из избранного
        '''
        product = self.get_object()
        user = request.user

        if request.method == 'POST':
            fav, created = Favorite.objects.get_or_create(user=user, product=product)
        else:
            Favorite.objects.filter(user=user, product=product).delete()
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
