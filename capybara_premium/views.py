from django.shortcuts import render
from .models import PremiumPlan, ProductPremium
from django.utils import timezone
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from .serializers import (
    PremiumPlanSerializer, 
    ProductPremiumSerializer, 
    ProductPremiumCreateSerializer   
)

from capybara_products.models import Product


class PremiumPlanViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API для работы с планами премиум-объявлений.
    
    Предоставляет возможность получать список доступных планов.
    """

    queryset = PremiumPlan.objects.filter(is_active=True)
    serializer_class = PremiumPlanSerializer
    ptrmission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        Получить список доступных премиум-планов.
        
        Требуется авторизация. Возвращает только активные планы.
        """
        return super().list(request, *args, **kwargs)
 

class ProductPremiumViewSet(viewsets.ViewSet):
    """
    API для работы с премиум-статусом продуктов.
    
    Предоставляет возможность активировать, получать информацию и отменять премиум-статус для продуктов.
    """
    permission_classes = [IsAuthenticated, IsAuthenticatedOrReadOnly]

    def get_product(self, pk):
        """Получает продукт по ID и проверяет права доступа"""
        product = get_object_or_404(Product, pk=pk)
        self.check_object_permissions(self.request, product)
        return product

    def retrieve(self, request, pk=None):
        """
        Получить информацию о премиум-статусе продукта.
        
        Возвращает детальную информацию о премиум-статусе продукта, включая выбранный план,
        даты начала и окончания, а также количество оставшихся дней.
        """
        product = self.get_product(pk)
        try:
            premium = ProductPremium.objects.get(product=product)
            serialaizer = ProductPremiumSerializer(premium)
            return Response(serialaizer.data)
        except ProductPremium.DoesNotExist:
                return Response({"detail": "У этого продукта нет премиум-статуса"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, pk=None):
        """
        Активировать премиум-статус для продукта.

        Требуется авторизация. Активирует премиум-статус для продукта на основе выбранного плана.
        """
        product = self.get_product(pk)

        serializer = ProductPremiumCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        plan = get_object_or_404(PremiumPlan, pk=serializer.validated_data['plan_id'])

        try:
            premium = ProductPremium.objects.get(product=product)
            premium.plan = plan
            premium.start_date = timezone.now()
            premium.end_date = premium.start_date + timezone.timedelta(days=plan.duration_days)
            premium.is_active = True
            premium.save()
        except ProductPremium.DoesNotExist:
            premium = ProductPremium.objects.create(
                product=product,
                plan=plan,
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=plan.duration_days),
                is_active=True
            )

        product.is_premium = True
        product.save()

        serializer = ProductPremiumSerializer(premium)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    

            


