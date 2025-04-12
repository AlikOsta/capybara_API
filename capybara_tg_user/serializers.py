from rest_framework import serializers
from .models import TelegramUser


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'telegram_id',
            'photo_url',
        ]
        read_only_fields = ['id', 'username', 'telegram_id']