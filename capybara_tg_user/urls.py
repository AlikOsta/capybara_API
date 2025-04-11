from django.urls import path
from .views import CurrencyAPIView


app_name = 'user'

urlpatterns = [
    path('api/v1/user/',  CurrencyAPIView.as_view()), #'currencies/api/v1/currency_list/',
]
