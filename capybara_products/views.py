
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Prefetch

from .models import Product, ProductView, Favorite, ProductComment, PremiumPlan, ProductPremium
from .serializers import (
    ProductListSerializer, 
    ProductDetailSerializer, 
    ProductCreateUpdateSerializer,
    ProductCommentCreateUpdateSerializer,
    ProductCommentSerializer,
    PremiumPlanSerializer, 
    ProductPremiumSerializer, 
    ProductPremiumCreateSerializer   
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


class ProductCommentViewSet(viewsets.ModelViewSet):
    """
    API для работы с комментариями к продуктам.
    
    Предоставляет возможность получать, создавать, обновлять и удалять комментарии к продуктам.
    Один пользователь может оставить только один комментарий к одному продукту.
    """

    permission_classes = [IsAuthenticated, IsCommentAuthorOrReadOnly]
    
    def get_queryset(self):
        """
        Возвращает комментарии для конкретного продукта.
        Для обычных пользователей возвращает только одобренные комментарии.
        Для автора продукта возвращает все комментарии.
        """
        
        product_id = self.kwargs.get('product_pk')
        queryset = ProductComment.objects.filter(product_id=product_id)
        
        product = get_object_or_404(Product, pk=product_id)
        
        if self.request.user != product.author:
            queryset = queryset.filter(status=3)
        
        return queryset.select_related('user')
    
    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от действия.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCommentCreateUpdateSerializer
        return ProductCommentSerializer
    
    def get_serializer_context(self):
        """
        Добавляет ID продукта в контекст сериализатора.
        """
        context = super().get_serializer_context()
        context['product_id'] = self.kwargs.get('product_pk')
        return context
    
    def perform_create(self, serializer):
        """
        Создает новый комментарий, связывая его с текущим пользователем и продуктом.
        """
        product_id = self.kwargs.get('product_pk')
        serializer.save(user=self.request.user, product_id=product_id)
    
    def list(self, request, *args, **kwargs):
        """
        Получить список комментариев к продукту.
        
        Для обычных пользователей возвращает только одобренные комментарии.
        Для автора продукта возвращает все комментарии.
        """
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """
        Создать комментарий к продукту.
        
        Требуется авторизация. Один пользователь может оставить только один комментарий к одному продукту.
        Комментарии проходят автоматическую модерацию.
        """
        return super().create(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Получить детальную информацию о комментарии.
        """
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Обновить комментарий (полное обновление).
        
        Требуется авторизация. Доступно только автору комментария.
        Обновленные комментарии проходят повторную модерацию.
        """
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Обновить комментарий (частичное обновление).
        
        Требуется авторизация. Доступно только автору комментария.
        Обновленные комментарии проходят повторную модерацию.
        """
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Удалить комментарий.
        
        Требуется авторизация. Доступно только автору комментария.
        """
        return super().destroy(request, *args, **kwargs)
    

# class PremiumPlanViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API для работы с планами премиум-объявлений.
    
    Предоставляет возможность получать список доступных планов.
    """

    queryset = PremiumPlan.objects.filter(is_active=True)
    serializer_class = PremiumPlanSerializer
    ptrmission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        Получить список доступных премиум-планов.
        
        Требуется авторизация. Возвращает только активные планы.
        """
        return super().list(request, *args, **kwargs)
 

# class ProductPremiumViewSet(viewsets.ViewSet):
    """
    API для работы с премиум-статусом продуктов.
    
    Предоставляет возможность активировать, получать информацию и отменять премиум-статус для продуктов.
    """
    permission_classes = [IsAuthenticated, IsAuthenticatedOrReadOnly]

    def get_product(self, pk):
        """Получает продукт по ID и проверяет права доступа"""
        product = get_object_or_404(Product, pk=pk)
        self.check_object_permissions(self.request, product)
        return product

    def retrieve(self, request, pk=None):
        """
        Получить информацию о премиум-статусе продукта.
        
        Возвращает детальную информацию о премиум-статусе продукта, включая выбранный план,
        даты начала и окончания, а также количество оставшихся дней.
        """
        product = self.get_product(pk)
        try:
            premium = ProductPremium.objects.get(product=product)
            serialaizer = ProductPremiumSerializer(premium)
            return Response(serialaizer.data)
        except ProductPremium.DoesNotExist:
                return Response({"detail": "У этого продукта нет премиум-статуса"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, pk=None):
        """
        Активировать премиум-статус для продукта.

        Требуется авторизация. Активирует премиум-статус для продукта на основе выбранного плана.
        """
        product = self.get_product(pk)

        serializer = ProductPremiumCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        plan = get_object_or_404(PremiumPlan, pk=serializer.validated_data['plan_id'])

        try:
            premium = ProductPremium.objects.get(product=product)
            premium.plan = plan
            premium.start_date = timezone.now()
            premium.end_date = premium.start_date + timezone.timedelta(days=plan.duration_days)
            premium.is_active = True
            premium.save()
        except ProductPremium.DoesNotExist:
            premium = ProductPremium.objects.create(
                product=product,
                plan=plan,
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=plan.duration_days),
                is_active=True
            )

        product.is_premium = True
        product.save()

        serializer = ProductPremiumSerializer(premium)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    

            

