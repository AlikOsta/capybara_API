from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

"""
GET /users/v1/users/

GET /users/v1/users/{pk}/

PUT /users/v1/users/{pk}/

PATCH /users/v1/users/{pk}/

"""


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/', include(router.urls)),
]