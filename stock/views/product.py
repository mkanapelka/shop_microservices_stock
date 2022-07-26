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
        name: str = self.request.query_params.get('name')
        min_cost: int = self.request.query_params.get('min_cost')
        max_cost: int = self.request.query_params.get('max_cost')
        min_quantity: int = self.request.query_params.get('min_quantity')
        max_quantity: int = self.request.query_params.get('max_quantity')
        product_status: Product.ProductStatus = self.request.query_params.get('status')
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

        if product_status is not None:
            queryset = queryset.filter(status=product_status)

        if category_name is not None:
            queryset = queryset.filter(category__name__startswith=category_name)

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
        min_value_validator = MinValueValidator(0, message='value must be over 0')
        values: list = self.__is_valid_line(line)
        Product.objects.create(name=values[ProductAdminApiViewSet.NAME_IDX],
                               cost=min_value_validator(int(values[ProductAdminApiViewSet.COST_IDX])),
                               quantity=min_value_validator(int(values[ProductAdminApiViewSet.QUANTITY_IDX])),
                               status=values[ProductAdminApiViewSet.STATUS_IDX],
                               category_id=int(values[ProductAdminApiViewSet.CATEGORY_ID_IDX]))

    def __is_valid_line(self, line: str) -> list:
        line.strip()
        if line is None or line == '':
            raise Exception("Incorrect line, please review file")
        values: list = line.split(ProductAdminApiViewSet.SEPARATOR)
        if len(values) != 5:
            raise Exception("Incorrect line, please review file")
        return values
