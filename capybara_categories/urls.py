
from django.urls import path
from .views import (
    CategoryAPIView, CategoryDetailAPIView, SubCategoryDetailAPIView
)

urlpatterns = [
    path('v1/', CategoryAPIView.as_view(), name='category-list'),
    path('v1/<slug:slug>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('v1/<slug:super_slug>/<slug:slug>/', SubCategoryDetailAPIView.as_view(), name='subcategory-detail'),
]