from rest_framework import serializers
from .models import Category, SubCategory
from capybara_products.models import Product
from capybara_products.serializers import ProductListSerializer


class CategoryListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'url') 
        extra_kwargs = {
            'url': {'view_name': 'category-detail', 'lookup_field': 'slug'}
        }


class SubCategorySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='category-detail',
        lookup_field='slug',
        lookup_url_kwarg='slug'
    )
    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'url')


class CategoryDetailSerializer(serializers.ModelSerializer):
    subcategory = CategoryListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'subcategory')


class SubCategoryDetailSerializer(serializers.ModelSerializer):
    category = serializers.ReadOnlyField(source='category.slug')
    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'slug', 'image', 'category')

