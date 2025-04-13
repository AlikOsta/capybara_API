from rest_framework import serializers
from django.urls import reverse
from .models import Product, ProductImage, Favorite, ProductComment

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
    main_image = serializers.ImageField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    product_url = serializers.HyperlinkedIdentityField(
        view_name='product-detail', lookup_field='pk')
    comments_count = serializers.SerializerMethodField()

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
    
    def get_comments_count(self, obj):
        """Возвращает количество одобренных комментариев к продукту"""
        return obj.comments.filter(status=3).count()


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
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_comments(self, obj):
        """
        Возвращает одобренные комментарии к продукту.
        Для автора продукта возвращает все комментарии.
        """
        request = self.context.get('request')
        queryset = obj.comments.all()
        
        if request and request.user != obj.author:
            queryset = queryset.filter(status=3)  
            
        return ProductCommentSerializer(
            queryset, 
            many=True, 
            context=self.context
        ).data


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


class ProductCommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для комментариев к продуктам.
    
    Предоставляет информацию о комментариях:
    - id: уникальный идентификатор комментария
    - user: информация о пользователе, оставившем комментарий
    - text: текст комментария
    - created_at: дата создания комментария
    - updated_at: дата обновления комментария
    """
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductComment
        fields = ['id', 'user', 'text', 'created_at', 'updated_at', 'status']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'status']
    
    def get_user(self, obj):
        """Возвращает базовую информацию о пользователе"""
        request = self.context.get('request')
        user_url = reverse('user-detail', kwargs={'pk': obj.user.pk})
        
        if request:
            user_url = request.build_absolute_uri(user_url)
            
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'photo_url': obj.user.photo_url,
            'user_url': user_url
        }


class ProductCommentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления комментариев к продуктам.
    
    Позволяет создавать и обновлять комментарии с указанием:
    - text: текст комментария
    """
    class Meta:
        model = ProductComment
        fields = ['text']
        
    def validate(self, data):
        """
        Проверяет, что пользователь не пытается создать второй комментарий к тому же продукту.
        """
        request = self.context.get('request')
        product_id = self.context.get('product_id')
        
        if self.instance is None:
            if ProductComment.objects.filter(user=request.user, product_id=product_id).exists():
                raise serializers.ValidationError(
                    "You have already commented on this product. Please update your existing comment."
                )
        
        return data