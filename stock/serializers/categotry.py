from rest_framework import serializers

from stock.models import Category
from stock.serializers.product import ProductSerializer


class CategorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=True)

    class Meta:
        model = Category
        fields = ('name', 'product')
