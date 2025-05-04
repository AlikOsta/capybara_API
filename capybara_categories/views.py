
    
from rest_framework import generics
from django.shortcuts import get_object_or_404
from .models import Category,  SubCategory

from .serializers import CategoryListSerializer, CategoryDetailSerializer, SubCategoryDetailSerializer


class CategoryAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer
    lookup_field = 'slug' 


class SubCategoryDetailAPIView(generics.RetrieveAPIView):
    serializer_class = SubCategoryDetailSerializer
    lookup_field = 'slug'

    def get_object(self):
        super_slug = self.kwargs['super_slug']
        sub_slug = self.kwargs['slug']
        return get_object_or_404(
            SubCategory,
            slug=sub_slug,
            super_rubric__slug=super_slug
        )