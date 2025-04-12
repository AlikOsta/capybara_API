from rest_framework import viewsets
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny
from django.db.models import Prefetch

from .models import Category
from .serializers import CategorySerializer, CategoryDetailSerializer
from capybara_products.models import Product

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /categories/v1/categories/       — список всех категорий
    GET /categories/v1/categories/{slug}/  — детали категории + список опубликованных объявлений
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

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategorySerializer
