from rest_framework import generics

from stock.models import Product, Category
from stock.serializers.product import ProductSerializer


class ProductApiView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        return self.__get_dynamic_queryset(queryset)

    def __get_dynamic_queryset(self, queryset):
        name: str = self.request.query_params.get('name')
        min_cost: int = self.request.query_params.get('min_cost')
        max_cost: int = self.request.query_params.get('max_cost')
        min_quantity: int = self.request.query_params.get('min_quantity')
        max_quantity: int = self.request.query_params.get('max_quantity')
        status: Product.ProductStatus = self.request.query_params.get('status')
        category_name: Category = self.request.query_params.get('category_name')
        if name is not None:
            queryset = queryset.filter(name__startswith=name)

        if min_cost is not None:
            queryset = queryset.filter(cost__gte=min_cost)

        if max_cost is not None:
            queryset = queryset.filter(cost__lte=max_cost)

        if min_quantity is not None:
            queryset = queryset.filter(quantity__gte=min_quantity)

        if max_quantity is not None:
            queryset = queryset.filter(quantity__lte=max_quantity)

        if status is not None:
            queryset = queryset.filter(status=status)

        if category_name is not None:
            queryset = queryset.filter(category__name__startswith=category_name)

        return queryset



