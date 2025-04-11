from django.urls import path
from .views import CurrenciesAPIView


app_name = 'currency'

urlpatterns = [
    path('api/v1/currencies-list/',  CurrenciesAPIView.as_view()), #'currencies/api/v1/currencies-list/',
]
