from rest_framework import generics

from stock.models import Characteristic
from stock.serializers.characteristic import CharacteristicSerializer


class CharacteristicApiView(generics.ListAPIView):
    serializer_class = CharacteristicSerializer

    def get_queryset(self):
        queryset = Characteristic.objects.all()

        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__startswith=name)

        return queryset
