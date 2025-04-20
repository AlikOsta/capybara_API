from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import UserViewSet, UserRatingViewSet

"""
GET /users/v1/users/
GET /users/v1/users/{pk}/
PUT /users/v1/users/{pk}/
PATCH /users/v1/users/{pk}/
"""

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

ratings_router = routers.NestedSimpleRouter(router, r'users', lookup='user')
# ratings_router.register(r'ratings', UserRatingViewSet, basename='user-rating')

urlpatterns = [
    path('v1/', include(router.urls)),
    # path('v1/', include(ratings_router.urls)),
]