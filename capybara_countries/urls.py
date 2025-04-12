from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CountryViewSet

"""
GET  /countries-cities/v1/countries/
GET  /countries-cities/v1/countries/{pk}/
"""

router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')

urlpatterns = [
    path('v1/', include(router.urls)),
]
