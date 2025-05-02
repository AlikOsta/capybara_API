from rest_framework import serializers
from django.urls import reverse
from .models import Product, ProductImage, Favorite
from django.utils import timezone


# user = serializers.HiddenField(default=serializers.CurrentUserDefault())


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для изображений продуктов.
    
    Предоставляет информацию об изображениях:
    - id: уникальный идентификатор изображения
    - image: файл изображения
    """
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка продуктов.
    
    Предоставляет основную информацию о продуктах для отображения в списках:
    - id: уникальный идентификатор продукта
    - title: название продукта
    - price: цена продукта
    - category: название категории продукта
    - currency: код валюты (например, USD, EUR)
    - main_image: основное изображение продукта
    - views_count: количество просмотров продукта
    - favorites_count: количество добавлений продукта в избранное
    - is_favorited: добавлен ли продукт в избранное текущим пользователем
    - product_url: ссылка на детальное представление продукта
    - create_at: дата создания продукта
    - status: статус продукта (1 - черновик, 2 - на модерации, 3 - опубликован)
    """
    category = serializers.CharField(source='category.name', read_only=True)
    currency = serializers.CharField(source='currency.code', read_only=True)
    city = serializers.CharField(source='city.name', read_only=True)
    country = serializers.CharField(source='country.name', read_only=True)
    author = serializers.CharField(source='author.username', read_only=True)
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
        """
        Определяет, добавлен ли продукт в избранное текущим пользователем.
        
        Использует оптимизированный запрос с prefetch_related, если доступен,
        иначе выполняет дополнительный запрос к базе данных.
        """
        user = self.context['request'].user

        if not user.is_authenticated:
            return False
        
        favs = getattr(obj, 'my_favorites', None)

        if favs is not None:
            return bool(favs)
        
        return obj.favorited_by.filter(user=user).exists()


class ProductDetailSerializer(ProductListSerializer):
    """
    Сериализатор для детального представления продукта.
    
    Расширяет ProductListSerializer, добавляя дополнительную информацию:
    - country: название страны
    - city: название города
    - author_name: имя пользователя автора
    - author_url: ссылка на профиль автора
    - description: полное описание продукта
    """
    country = serializers.CharField(source='country.name', read_only=True)
    city = serializers.CharField(source='city.name', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_url = serializers.HyperlinkedRelatedField(
        view_name='user-detail', read_only=True, source='author')

    class Meta:
        model = Product
        fields = "__all__"


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления продуктов.
    
    Позволяет создавать и обновлять продукты с указанием:
    - category: категория продукта
    - title: название продукта
    - description: описание продукта
    - country: страна
    - city: город
    - price: цена
    - currency: валюта
    - status: статус продукта (1 - черновик, 2 - на модерации, 3 - опубликован)
    - images: изображение продукта (в текущей версии поддерживается загрузка одного изображения)
    
    Поля author, views_count и favorites_count являются только для чтения и устанавливаются автоматически.
    """
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
        """
        Проверяет валидность данных перед созданием или обновлением продукта.
        """
        return data

    def create(self, validated_data):
        """
        Создает новый продукт и связанное с ним изображение.
        
        Автоматически устанавливает текущего пользователя как автора продукта.
        """
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
        """
        Обновляет существующий продукт и добавляет новые изображения, если они предоставлены.
        """
        images_data = validated_data.pop('images', [])
        product = super().update(instance, validated_data)

        for img in images_data:
            ProductImage.objects.create(product=product, image=img)

        return product

 