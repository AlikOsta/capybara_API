from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Country
from .serializers import CountrySerializer, CountryDetailSerializer


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для работы со странами и городами.
    
    Предоставляет доступ только для чтения к списку стран и детальной информации
    о конкретной стране, включая список городов в ней.
    """
    queryset = Country.objects.all().prefetch_related('cities')
    permission_classes = [AllowAny]
    lookup_field = 'pk'  

    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от действия.
        
        Для детального представления используется CountryDetailSerializer,
        для списка - CountrySerializer.
        """
        if self.action == 'retrieve':
            return CountryDetailSerializer
        return CountrySerializer
