from rest_framework import serializers
from .models import Currency


class CurrenciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'name')