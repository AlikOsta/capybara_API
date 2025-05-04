from django.urls import path
from .views import CurrencyViewSet

"""
GET  /currencies/v1/currencies/
"""


urlpatterns = [
    path('v1/', CurrencyViewSet.as_view({'get': 'list'}), name='currencies-list'),
]
