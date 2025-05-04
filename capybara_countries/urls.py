from django.urls import path
from .views import CountryViewSet

urlpatterns = [
    path('v1/', CountryViewSet.as_view({'get': 'list'}), name='country-list'),
    path('v1/<int:pk>/', CountryViewSet.as_view({'get': 'retrieve'}), name='country-detail'),
]
