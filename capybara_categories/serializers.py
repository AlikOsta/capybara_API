from rest_framework import serializers

from .models import Category
from capybara_products.models import Product
from capybara_products.serializers import ProductListSerializer


class CategorySerializer(serializers.ModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='category-detail',
        lookup_field='slug'
    )

    count = serializers.CharField(source='get_count_products', read_only=True)


    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'url', 'count']


class CategoryDetailSerializer(CategorySerializer):
    products = ProductListSerializer(many=True, read_only=True)

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ['products']
