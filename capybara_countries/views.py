from django.shortcuts import render
from rest_framework import generics

from .models import Country, City
from .serializers import CountriesSerializer


class CountriesAPIView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountriesSerializer