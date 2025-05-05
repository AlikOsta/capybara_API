from rest_framework import serializers
from .models import TelegramUser, UserRating
from django.db.models import Avg, Count

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

    user_url = serializers.HyperlinkedIdentityField(view_name='user-detail', lookup_field='pk')
    products = ProductListSerializer(many=True, read_only=True, source='product_set')
    average_rating = serializers.FloatField(read_only=True)
    ratings_count = serializers.IntegerField(read_only=True)
    my_rating = serializers.SerializerMethodField()

    class Meta:
        model = TelegramUser
        fields = ['id', 'username', 'first_name', 'last_name',
            'telegram_id', 'photo_url', 'user_url', 'products',
            'average_rating', 'ratings_count', 'my_rating']
        
        read_only_fields = ['id', 'username', 'telegram_id']

    def get_my_rating(self, obj):
        """
        Возвращает оценку, которую текущий пользователь оставил этому пользователю,
        или None, если оценки нет
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            rating = UserRating.objects.get(from_user=request.user, to_user=obj)
            return {
                'id': rating.id,
                'rating': rating.rating,
                'comment': rating.comment
            }
        except UserRating.DoesNotExist:
            return None
        
    def get_queryset(self):
        """
        Возвращает QuerySet пользователей с аннотациями для рейтинга.
        """
        return TelegramUser.objects.annotate(
            average_rating=Avg('received_ratings__rating'),
            ratings_count=Count('received_ratings', distinct=True)
        )


class UserRatingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения рейтингов пользователей
    """
    from_user = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRating
        fields = ['id', 'from_user', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'from_user', 'created_at', 'updated_at']
    
    def get_from_user(self, obj):
        """Возвращает базовую информацию о пользователе, оставившем оценку"""
        return {
            'id': obj.from_user.id,
            'username': obj.from_user.username,
            'photo_url': obj.from_user.photo_url,
        }
    

class UserRatingCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рейтингов пользователей
    """
    class Meta:
        model = UserRating
        fields = ['rating', 'comment']
    
    def validate(self, data):
        """
        Проверяет, что пользователь не пытается оценить сам себя
        """
        request = self.context.get('request')
        to_user_id = self.context.get('to_user_id')
        
        if request.user.id == int(to_user_id):
            raise serializers.ValidationError(
                "Вы не можете оценить сами себя"
            )
        
        return data