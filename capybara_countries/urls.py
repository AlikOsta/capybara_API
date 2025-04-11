from django.urls import path
from .views import CountriesAPIView


app_name = 'country'

urlpatterns = [
    path('api/v1/countries-cities-list/',  CountriesAPIView.as_view()), #'countries-cities/api/v1/countries-cities-list/',
]
