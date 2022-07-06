from typing import io

from django.db import transaction
from rest_framework import mixins, serializers, status
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet

from stock.models import Product, Category
from stock.serializers.product import ProductSerializer


class ProductApiViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def filter_queryset(self, queryset):
        queryset = Product.objects.all()
        return self.__get_dynamic_queryset(queryset)

    @action(methods=['patch'], detail=True)
    def update_quantity(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        product: Product = Product.objects.get(pk=pk)
        received_quantity: int = request.data['quantity']

        if self.__quantity_validation(received_quantity):

            new_quantity: int = product.quantity + received_quantity
            if new_quantity < 0:
                raise "Not enough quantity at stock"
            product.quantity = new_quantity
            product = product.save()
        return Response(product)

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

    def __quantity_validation(self, received_quantity: int) -> bool:
        if type(received_quantity) != int:
            raise serializers.ValidationError("Quantity must be int")
        if received_quantity is None:
            raise serializers.ValidationError("Quantity must be")
        return True


class ProductAdminApiViewSet(GenericViewSet):
    SEPARATOR: str = ';'
    queryset = Product.objects.all()
    parser_classes = (MultiPartParser,)

    @transaction.atomic()
    @action(methods=['put'], url_path='upload', detail=True)
    def add_products_from_file(self, request, *args, **kwargs):
        file_uploaded = request.FILES.get('file')
        if file_uploaded is None:
            raise Exception("File wasn't uploaded")
        self.__processing_uploaded_file(file_uploaded)
        return Response(status=status.HTTP_200_OK)

    def __processing_uploaded_file(self, file: io.BinaryIO) -> None:
        try:
            for line in file.readlines():
                self.__processing_product_line(line.decode('utf-8'))
        finally:
            file.close()

    def __processing_product_line(self, line: str) -> None:
        values: list = self.__is_valid_line(line)
        Product.objects.create(name=values[0],
                               cost=int(values[1]),
                               quantity=int(values[2]),
                               status=values[3],
                               category_id=int(values[4]))

    def __is_valid_line(self, line: str) -> list:
        line.strip()
        if line is None or line == '':
            raise Exception("Incorrect line, please review file")
        values: list = line.split(ProductAdminApiViewSet.SEPARATOR)
        if len(values) != 5:
            raise Exception("Incorrect line, please review file")
        return values
