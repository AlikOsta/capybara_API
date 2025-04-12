from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Country
from .serializers import CountrySerializer, CountryDetailSerializer


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET  /countries-cities/v1/countries/        — список стран
    GET  /countries-cities/v1/countries/{pk}/   — детали страны + её города
    """
    queryset = Country.objects.all().prefetch_related('cities')
    permission_classes = [AllowAny]
    lookup_field = 'pk'  

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CountryDetailSerializer
        return CountrySerializer