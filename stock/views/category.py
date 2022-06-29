from rest_framework import generics

from stock.models import Category
from stock.serializers.categotry import CategorySerializer


class CategoryApiView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()

        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__startswith=name)

        return queryset
