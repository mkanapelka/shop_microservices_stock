from typing import io

from django.db import transaction
from django.core.validators import MinValueValidator
from rest_framework import mixins, serializers, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from stock.models import Product, Category
from stock.serializers.product import ProductSerializer


class ProductApiViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (JSONParser,)

    def filter_queryset(self, queryset):
        queryset = Product.objects.all()
        return self.__get_dynamic_queryset(queryset)

    @action(methods=['patch'], detail=True)
    def update_quantity(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        product: Product = Product.objects.get(pk=pk)
        received_quantity: int = request.data.get('quantity', None)

        if self.__quantity_validation(received_quantity):
            new_quantity: int = product.quantity + received_quantity
            if new_quantity < 0:
                raise Exception("Not enough quantity at stock")
            product.quantity = new_quantity
            product = product.save()
        return Response(product)

    def __get_dynamic_queryset(self, queryset):
        product_like_parameters: tuple = ('name', 'category_name')
        product_gte_parameters: tuple = ('min_cost', 'min_quantity')
        product_lte_parameters: tuple = ('max_cost', 'max_quantity')
        product_eq_parameters: tuple = ('status',)
        prefix_for_gte_parameters: str = 'min_'
        prefix_for_lte_parameters: str = 'max_'
        for name_of_param, param in self.request.query_params.items():
            if name_of_param in product_like_parameters:
                queryset = queryset.filter((name_of_param + "__startswith", param))
            if name_of_param in product_gte_parameters:
                queryset = queryset.filter((name_of_param[len(prefix_for_gte_parameters):] + "__gte", param))
            if name_of_param in product_lte_parameters:
                queryset = queryset.filter((name_of_param[len(prefix_for_lte_parameters):] + "__lte", param))
            if name_of_param in product_eq_parameters:
                queryset = queryset.filter((name_of_param, param))
        return queryset

    def __quantity_validation(self, received_quantity: int) -> bool:
        if received_quantity is None:
            raise serializers.ValidationError("Quantity didn't receive")
        if type(received_quantity) != int:
            raise serializers.ValidationError("Quantity must be int")
        return True


class ProductAdminApiViewSet(GenericViewSet):
    SEPARATOR: str = ';'
    NAME_IDX: int = 0
    COST_IDX: int = 1
    QUANTITY_IDX: int = 2
    STATUS_IDX: int = 3
    CATEGORY_ID_IDX: int = 4

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser,)

    @transaction.atomic(durable=True)
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
        Product.objects.create(name=values[ProductAdminApiViewSet.NAME_IDX],
                               cost=int(values[ProductAdminApiViewSet.COST_IDX]),
                               quantity=int(values[ProductAdminApiViewSet.QUANTITY_IDX]),
                               status=values[ProductAdminApiViewSet.STATUS_IDX],
                               category_id=int(values[ProductAdminApiViewSet.CATEGORY_ID_IDX]))

    def __is_valid_line(self, line: str) -> list:
        min_value_validator = MinValueValidator(0, message='value must be over 0')
        line.strip()
        if line is None or line == '':
            raise Exception("Incorrect line, please review file")
        values: list = line.split(ProductAdminApiViewSet.SEPARATOR)
        if len(values) != 5:
            raise Exception("Incorrect line, please review file")
        cost: int = int(values[ProductAdminApiViewSet.COST_IDX])
        quantity: int = int(values[ProductAdminApiViewSet.QUANTITY_IDX])
        min_value_validator(cost)
        min_value_validator(quantity)
        return values
