from rest_framework import serializers
from .models import Category
from capybara_products.models import Product
from capybara_products.serializers import ProductListSerializer


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка категорий.
    
    Предоставляет базовую информацию о категориях, включая:
    - id: уникальный идентификатор категории
    - name: название категории
    - slug: URL-совместимый идентификатор категории
    - image: изображение категории
    - url: ссылка на детальное представление категории
    - count: количество опубликованных продуктов в категории
    """

    url = serializers.HyperlinkedIdentityField(
        view_name='category-detail',
        lookup_field='slug'
    )

    count = serializers.CharField(source='get_count_products', read_only=True)
    
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            # Исправляем путь, удаляя лишнее "media/"
            return obj.image.url.replace('/media/media/', '/media/')
        return None

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'url', 'count']


class CategoryDetailSerializer(CategorySerializer):
    """
    Сериализатор для детального представления категории.
    
    Расширяет базовый CategorySerializer, добавляя список продуктов,
    относящихся к данной категории. Включает только опубликованные продукты.
    
    Дополнительные поля:
    - products: список продуктов в категории, представленных через ProductListSerializer
    """
    
    products = ProductListSerializer(many=True, read_only=True)

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ['products']
