from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

"""
GET/POST    /products/v1/products/
GET/PUT/... /products/v1/products/{pk}
GET         /products/v1/products/favorites/
"""

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('v1/', include(router.urls)),
]
