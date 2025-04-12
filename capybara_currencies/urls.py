from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CurrencyViewSet

"""
GET  /currencies/v1/currencies/
"""

router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet, basename='currency')

urlpatterns = [
    path('v1/', include(router.urls)),
]
