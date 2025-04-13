from django.contrib import admin
from .models import Product, ProductImage, Favorite, ProductComment


admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Favorite)
admin.site.register(ProductComment)

