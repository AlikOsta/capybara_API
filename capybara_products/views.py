from django.shortcuts import render
from rest_framework import generics

from .models import Product
from .serializers import ProductsSerializer


class ProductsAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductsSerializer


