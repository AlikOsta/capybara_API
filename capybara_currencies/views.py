from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Currency
from .serializers import CurrencySerializer

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /currencies/v1/currencies/       — список валют
    """
    
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [AllowAny]
