from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet


"""
GET  /categories/v1/categories/

GET  /categories/v1/categories/{slug}/
"""

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')


urlpatterns = [
    path('v1/', include(router.urls)),
]
