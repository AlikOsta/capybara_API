from rest_framework import serializers
from django.urls import reverse
from .models import Product, ProductImage, Favorite


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    currency = serializers.CharField(source='currency.code', read_only=True)
    main_image = serializers.ImageField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = fields = "__all__"

    def get_is_favorited(self, obj):

        user = self.context['request'].user

        if not user.is_authenticated:
            return False
        
        favs = getattr(obj, 'my_favorites', None)

        if favs is not None:
            return bool(favs)
        
        return obj.favorited_by.filter(user=user).exists()


class ProductDetailSerializer(ProductListSerializer):
    country = serializers.CharField(source='country.name', read_only=True)
    city = serializers.CharField(source='city.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('category', 'title', 'description', 'country', 'city', 'price', 'currency')

    def validate(self, data):
        return data

    def create(self, validated_data):
        return Product.objects.create(**validated_data)
