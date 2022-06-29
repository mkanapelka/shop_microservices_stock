from rest_framework import serializers

from stock.models import Characteristic


class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = ('name',)
