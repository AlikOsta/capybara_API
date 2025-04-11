from django.shortcuts import render
from rest_framework import generics

from .models import Category
from .serializers import CategoriesSerializer, CategoryDetailSerializer


class CategoriesAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.prefetch_related('products')
    serializer_class = CategoryDetailSerializer
    lookup_field = 'slug'