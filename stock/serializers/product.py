from rest_framework import serializers

from stock.models import Product
from stock.serializers.categotry import CategorySerializer


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(required=True)

    class Meta:
        model = Product
        fields = ('name', 'cost', 'quantity', 'status', 'category')
