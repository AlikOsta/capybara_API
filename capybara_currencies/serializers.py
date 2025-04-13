from rest_framework import serializers
from .models import Currency

class CurrencySerializer(serializers.ModelSerializer):
    """
    Сериализатор для валют.
    
    Предоставляет информацию о валютах:
    - id: уникальный идентификатор валюты
    - name: полное название валюты
    - code: код валюты (например, USD, EUR, RUB)
    - order: порядок сортировки валюты в списке
    """
    class Meta:
        model = Currency
        fields = ['id', 'name', 'code', 'order']
