from django.conf import settings
from django.conf.urls.static import static
from rest_framework_nested import routers

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, FavoriteViewSet, ProductCommentViewSet

"""
    GET    /products/v1/products/             — список (только status=3, + свои для авториз.)
    POST   /products/v1/products/             — создать новое объявление

    GET    /products/v1/products/{pk}/        — детали + сохраняем просмотр
    PUT    /products/v1/products/{pk}/        — полный апдейт (только автор)
    PATCH  /products/v1/products/{pk}/        — частичный апдейт (только автор)
    DELETE /products/v1/products/{pk}/        — удалить (только автор)

    GET    /products/v1/products/favorites/   — список избранного текущего пользователя
    POST   /products/v1/products/{pk}/favorite/   — добавить в избранное
    DELETE /products/v1/products/{pk}/favorite/   — убрать из избранного
"""

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
# router.register(r'favorites', FavoriteViewSet, basename='favorite')

comments_router = routers.NestedSimpleRouter(router, r'products', lookup='product')
# comments_router.register(r'comments', ProductCommentViewSet, basename='product-comment')


urlpatterns = [
    path('v1/', include(router.urls)),
    # path('v1/', include(comments_router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
