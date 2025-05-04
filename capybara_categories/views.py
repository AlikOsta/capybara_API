
    
from rest_framework import generics
from django.shortcuts import get_object_or_404
from .models import Category,  SubCategory

from .serializers import CategoryListSerializer, CategoryDetailSerializer, SubCategoryDetailSerializer


class CategoryAPIView(generics.ListAPIView):
    """
    API для просмотра категорий.

    """
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class CategoryDetailAPIView(generics.RetrieveAPIView):
    """
    API для просмотра деталей категории.

    """
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer
    lookup_field = 'slug' 


class SubCategoryDetailAPIView(generics.RetrieveAPIView):
    """
    API для просмотра детелей подкатегории.

    """
    serializer_class = SubCategoryDetailSerializer
    lookup_field = 'slug'

    def get_object(self):
        super_slug = self.kwargs['super_slug']
        sub_slug = self.kwargs['slug']
        return get_object_or_404(
            SubCategory,
            slug=sub_slug,
            category__slug=super_slug,
            
        )