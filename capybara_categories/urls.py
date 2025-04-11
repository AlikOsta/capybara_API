from django.urls import path
from .views import CategoriesAPIView, CategoryDetailAPIView


app_name = 'category'

urlpatterns = [
    path('api/v1/categories-list/', CategoriesAPIView.as_view(), name='categories_list'), #'categories/api/v1/categories-list/',
    path('api/v1/category/<slug:slug>/', CategoryDetailAPIView.as_view(), name='category-detail'),
]
