from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import UserViewSet, UserRatingViewSet, TelegramAuthView, TokenRefreshFromCookieView

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
    path('v1/auth/telegram/', TelegramAuthView.as_view(), name='telegram-auth'),
    path('v1/auth/refresh/', TokenRefreshFromCookieView.as_view(), name='token-refresh'),
]