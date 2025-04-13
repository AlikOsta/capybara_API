from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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

    @swagger_auto_schema(
        operation_summary="Получить список стран",
        operation_description="Возвращает список всех стран с базовой информацией",
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=CountrySerializer(many=True)
            ),
        },
        tags=['Countries & Cities']
    )
    def list(self, request, *args, **kwargs):
        """
        Получить список всех стран.
        
        Возвращает список всех стран с их основными атрибутами.
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить детальную информацию о стране",
        operation_description="Возвращает детальную информацию о стране и список городов в ней",
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                description='Уникальный идентификатор страны',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=CountryDetailSerializer()
            ),
            404: "Страна не найдена"
        },
        tags=['Countries & Cities']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Получить детальную информацию о стране по её идентификатору.
        
        Возвращает информацию о стране и список городов,
        относящихся к этой стране.
        """
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от действия.
        
        Для детального представления используется CountryDetailSerializer,
        для списка - CountrySerializer.
        """
        if self.action == 'retrieve':
            return CountryDetailSerializer
        return CountrySerializer
