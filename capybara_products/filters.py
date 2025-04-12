from django_filters import rest_framework as filters
from .models import Product

class ProductFilterSet(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    
    class Meta:
        model = Product
        fields = {
            'country': ['exact'],
            'city': ['exact'],
            'currency': ['exact'],
            'category': ['exact'],
            'status': ['exact'],
        }
