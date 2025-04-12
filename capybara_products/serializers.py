from rest_framework import serializers
from django.urls import reverse
from .models import Product, ProductImage, Favorite


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True)
    currency = serializers.CharField(source='currency.code', read_only=True)
    main_image = serializers.ImageField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    product_url = serializers.HyperlinkedIdentityField(
        view_name='product-detail', lookup_field='pk')

    class Meta:
        model = Product
        fields = "__all__"

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
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_url = serializers.HyperlinkedRelatedField(
        view_name='user-detail', read_only=True, source='author')


    class Meta:
        model = Product
        fields = "__all__"


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    # images = serializers.ListField(
    #     child=serializers.ImageField(),
    #     write_only=True,
    #     required=False
    # )

    # пока только одна картинка
    images = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = (
            'category', 'title', 'description',
            'country', 'city', 'price', 'currency', 'status',
            'images',
        )
        read_only_fields = ['author', 'views_count', 'favorites_count']

    def validate(self, data):
        return data

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        # ставим автора
        validated_data['author'] = self.context['request'].user
        product = super().create(validated_data)

        # # создаём отдельные записи ProductImage — тут вызовется save() и process_image
        # for img in images_data:
        #     ProductImage.objects.create(product=product, image=img)

        ProductImage.objects.create(product=product, image=images_data)
        return product

    def update(self, instance, validated_data):

        images_data = validated_data.pop('images', [])
        product = super().update(instance, validated_data)

        for img in images_data:
            ProductImage.objects.create(product=product, image=img)

        return product
