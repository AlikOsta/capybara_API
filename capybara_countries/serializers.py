from rest_framework import serializers
from .models import Country, City

class CitySerializer(serializers.ModelSerializer):
    """
    Сериализатор для городов.
    
    Предоставляет базовую информацию о городах:
    - id: уникальный идентификатор города
    - name: название города
    """
    class Meta:
        model = City
        fields = ['id', 'name']


class CountrySerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка стран.
    
    Предоставляет базовую информацию о странах:
    - id: уникальный идентификатор страны
    - name: название страны
    - url: ссылка на детальное представление страны
    """
    class Meta:
        model = Country
        fields = ['id', 'name', 'url']
        

class CountryDetailSerializer(CountrySerializer):
    """
    Сериализатор для детального представления страны.
    
    Расширяет базовый CountrySerializer, добавляя список городов,
    относящихся к данной стране.
    
    Дополнительные поля:
    - cities: список городов в стране, представленных через CitySerializer
    """
    cities = CitySerializer(many=True, read_only=True)

    class Meta(CountrySerializer.Meta):
        fields = CountrySerializer.Meta.fields + ['cities']
