from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny

from .models import Currency
from .serializers import CurrencySerializer

class CurrencyViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API для работы с валютами.
    
    Предоставляет доступ только для чтения к списку валют, используемых в системе.
    Валюты используются при создании и отображении продуктов.
    """
    
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [AllowAny]
