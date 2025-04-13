from rest_framework import serializers
from .models import TelegramUser

from capybara_products.serializers import ProductListSerializer


class TelegramUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователей Telegram.
    
    Предоставляет информацию о пользователях:
    - id: уникальный идентификатор пользователя в системе
    - username: имя пользователя в Telegram
    - first_name: имя пользователя
    - last_name: фамилия пользователя
    - telegram_id: уникальный идентификатор пользователя в Telegram
    - photo_url: URL фотографии пользователя
    - user_url: ссылка на детальное представление пользователя
    - products: список продуктов, созданных пользователем
    """

    user_url = serializers.HyperlinkedIdentityField(
        view_name='user-detail',
        lookup_field='pk'
    )

    products = ProductListSerializer(many=True, read_only=True, source='product_set')

    class Meta:
        model = TelegramUser
        fields = ['id', 'username', 'first_name', 'last_name',
            'telegram_id', 'photo_url', 'user_url', 'products']
        
        read_only_fields = ['id', 'username', 'telegram_id']
