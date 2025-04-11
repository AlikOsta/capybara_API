from rest_framework import serializers

from .models import Product
from .models import ProductImage
from .models import ProductView

from capybara_countries.serializers import CountriesSerializer
# from capybara_categories.serializers import CategoriesSerializer
from capybara_currencies.serializers import CurrenciseSerializer


class ProductViewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductView
        fields = ('id', 'product',)


class ProductsSerializer(serializers.ModelSerializer):
    country = CountriesSerializer(read_only=True)
    # category = CategoriesSerializer(read_only=True)
    currency = CurrenciseSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'title', 'price', 'currency', 'category', 'country', 'status', 'create_at')