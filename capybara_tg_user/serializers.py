from rest_framework import serializers
from .models import TelegramUser


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = TelegramUser
        fields = ('id', 'username', 'first_name', 'last_name', 'telegram_id', 'date_joined', 'is_staff', 'is_active', 'groups')