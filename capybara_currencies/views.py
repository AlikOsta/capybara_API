from django.shortcuts import render
from rest_framework import generics

from .models import Currency
from .serializers import CurrenciseSerializer


class CurrenciesAPIView(generics.ListAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrenciseSerializer