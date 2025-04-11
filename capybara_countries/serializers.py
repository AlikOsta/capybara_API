from rest_framework import serializers
from .models import Country, City

from capybara_currencies.serializers import CurrenciseSerializer


class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class CountriesSerializer(serializers.ModelSerializer):
    cities = CitiesSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = ['id', 'name', 'cities']