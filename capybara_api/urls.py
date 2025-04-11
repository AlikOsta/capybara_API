
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('categories/', include('capybara_categories.urls')),
    path('countries-cities/', include('capybara_countries.urls')),
    path('currencies/', include('capybara_currencies.urls')),
    path('products/', include('capybara_products.urls')),
    path('users/', include('capybara_tg_user.urls')),

]
