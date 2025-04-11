from django.urls import path
from .views import ProductsAPIView


app_name = 'product'

urlpatterns = [
    path('api/v1/products-list/',  ProductsAPIView.as_view()), #'products/api/v1/products-list/',
]
