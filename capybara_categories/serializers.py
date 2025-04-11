from rest_framework import serializers
from .models import Category

from capybara_products.serializers import ProductsSerializer


class CategoriesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'url')

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None

    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()
    

class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductsSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'products']