from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
   openapi.Info(
      title="Capybara API",
      default_version='v1',
      description="API маркетплейса Capybara",
      terms_of_service="https://capybarashop.store",
      contact=openapi.Contact(email="ostrovanaleksei@gmail.com"),

   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('categories/', include('capybara_categories.urls')),
    path('countries/', include('capybara_countries.urls')),
    path('currencies/', include('capybara_currencies.urls')),
    path('products/', include('capybara_products.urls')),
    path('users/', include('capybara_tg_user.urls')),
    
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)