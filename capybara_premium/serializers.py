from rest_framework import serializers
from .models import PremiumPlan, ProductPremium
from django.utils import timezone


class PremiumPlanSerializer(serializers.ModelSerializer):
    """
    Сериализатор для планов премиум-подписки.

    Предоставляет информацию о плане премиум-подписки:
    - id: уникальный идентификатор плана
    - name: название плана
    - description: описание плана
    - price: цена плана
    - duration_days: продолжительность плана (в днях)
    """
    class Meta:
        model = PremiumPlan
        fields = ['id', 'name', 'description', 'price', 'duration_days']


class ProductPremiumSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации о премиум-статусе продукта

    """
    plan = PremiumPlanSerializer(read_only=True)
    days_left = serializers.SerializerMethodField()

    class Meta:
        model = ProductPremium
        fields = '__all__'

    def get_days_left(self, obj) -> int:
        """
        Возвращает количество дней, оставшихся до окончания премиум-статуса продукта.
        """
        if not obj.end_date:
            return 0
        
        now = timezone.now()

        if obj.end_date <= now:
            return 0
        
        delta = obj.end_date - now
        return delta.days
    

class ProductPremiumCreateSerializer(serializers.Serializer):
    """
    Сериализатор для активации премиум-статуса продукта
    """

    plan_id = serializers.IntegerField()

    def validate_plan_id(self, value):
        try:
            plan = PremiumPlan.objects.get(pk=value, is_active=True)
            return plan 
        except PremiumPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid plan ID")
        
    