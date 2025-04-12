from rest_framework import serializers
from .models import TelegramUser

from  capybara_products.serializers import ProductListSerializer


class TelegramUserSerializer(serializers.ModelSerializer):

    user_url = serializers.HyperlinkedIdentityField(
        view_name='user-detail',
        lookup_field='pk'
    )

    products = ProductListSerializer(many=True, read_only=True, source='product_set')

    class Meta:
        model = TelegramUser
        fields = [ 'id', 'username', 'first_name', 'last_name',
            'telegram_id', 'photo_url', 'user_url', 'products' ]
        
        read_only_fields = ['id', 'username', 'telegram_id']