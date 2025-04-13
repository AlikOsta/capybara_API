from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Currency
from .serializers import CurrencySerializer

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для работы с валютами.
    
    Предоставляет доступ только для чтения к списку валют, используемых в системе.
    Валюты используются при создании и отображении продуктов.
    """
    
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Получить список валют",
        operation_description="Возвращает список всех валют, доступных в системе",
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=CurrencySerializer(many=True)
            ),
        },
        tags=['Currencies']
    )
    def list(self, request, *args, **kwargs):
        """
        Получить список всех валют.
        
        Возвращает список всех валют с их кодами и названиями.
        Валюты отсортированы по полю order.
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить информацию о валюте",
        operation_description="Возвращает детальную информацию о конкретной валюте по её идентификатору",
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                description='Уникальный идентификатор валюты',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=CurrencySerializer()
            ),
            404: "Валюта не найдена"
        },
        tags=['Currencies']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Получить детальную информацию о валюте по её идентификатору.
        
        Возвращает информацию о конкретной валюте, включая её код и название.
        """
        return super().retrieve(request, *args, **kwargs)
