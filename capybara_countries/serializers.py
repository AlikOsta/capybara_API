from rest_framework import serializers
from .models import Country, City

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ['id', 'name', 'url']
        

class CountryDetailSerializer(CountrySerializer):
    cities = CitySerializer(many=True, read_only=True)

    class Meta(CountrySerializer.Meta):
        fields = CountrySerializer.Meta.fields + ['cities']