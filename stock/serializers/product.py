from rest_framework import serializers

from stock.models import Product


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('name', 'cost', 'quantity', 'status')
