from abc import ABC, abstractmethod
from typing import io

from django.core.validators import MinValueValidator
from django.db.models import QuerySet
from rest_framework import serializers

from stock.models import Product


class ProductService(ABC):
    SEPARATOR: str = ';'
    NAME_IDX: int = 0
    COST_IDX: int = 1
    QUANTITY_IDX: int = 2
    STATUS_IDX: int = 3
    CATEGORY_ID_IDX: int = 4

    PRODUCT_LIKE_PARAMETERS: tuple = ('name', 'category_name')
    PRODUCT_GTE_PARAMETERS: tuple = ('min_cost', 'min_quantity')
    PRODUCT_LTE_PARAMETERS: tuple = ('max_cost', 'max_quantity')
    PRODUCT_EQ_PARAMETERS: tuple = ('status',)
    PREFIX_FOR_GTE_PARAMETER: str = 'min_'
    PREFIX_FOR_LTE_PARAMETER: str = 'max_'

    @abstractmethod
    def get_dynamic_queryset(self, request, queryset: QuerySet) -> QuerySet:
        pass

    @abstractmethod
    def update_quantity(self, request, *args, **kwargs):
        pass

    @abstractmethod
    def add_products_from_file(self, request, *args, **kwargs):
        pass


class ProductServiceImpl(ProductService):
    def get_dynamic_queryset(self, request, queryset: QuerySet) -> QuerySet:
        len_min_prefix: int = len(ProductService.PREFIX_FOR_LTE_PARAMETER)
        len_max_prefix: int = len(ProductService.PREFIX_FOR_GTE_PARAMETER)

        for name_of_param, param in request.query_params.items():
            if name_of_param in self.PRODUCT_LIKE_PARAMETERS:
                queryset = queryset.filter((name_of_param + "__startswith", param))
            if name_of_param in self.PRODUCT_GTE_PARAMETERS:
                queryset = queryset.filter((name_of_param[len_min_prefix:] + "__gte", param))
            if name_of_param in self.PRODUCT_LTE_PARAMETERS:
                queryset = queryset.filter((name_of_param[len_max_prefix:] + "__lte", param))
            if name_of_param in self.PRODUCT_EQ_PARAMETERS:
                queryset = queryset.filter((name_of_param, param))
        return queryset

    def update_quantity(self, request, *args, **kwargs) -> Product:
        pk: int = kwargs.get('pk')
        product: Product = Product.objects.get(pk=pk)
        received_quantity: int = request.data.get('quantity', None)

        if self.__quantity_validation(received_quantity):
            new_quantity: int = product.quantity + received_quantity
            if new_quantity < 0:
                raise Exception("Not enough quantity at stock")
            product.quantity = new_quantity
            product = product.save()
        return product

    def add_products_from_file(self, request, *args, **kwargs):
        # TODO: refactor this
        file_uploaded = request.request.FILES.get('file')
        if file_uploaded is None:
            raise Exception("File wasn't uploaded")
        self.__processing_uploaded_file(file_uploaded)
        pass

    def __quantity_validation(self, received_quantity: int) -> bool:
        if received_quantity is None:
            raise serializers.ValidationError("Quantity didn't receive")
        if type(received_quantity) != int:
            raise serializers.ValidationError("Quantity must be int")
        return True

    def __processing_uploaded_file(self, file: io.BinaryIO) -> None:
        try:
            for line in file.readlines():
                self.__processing_product_line(line.decode('utf-8'))
        finally:
            file.close()

    def __processing_product_line(self, line: str) -> None:
        values: list = self.__is_valid_line(line)
        Product.objects.create(name=values[self.NAME_IDX],
                               cost=int(values[self.COST_IDX]),
                               quantity=int(values[self.QUANTITY_IDX]),
                               status=values[self.STATUS_IDX],
                               category_id=int(values[self.CATEGORY_ID_IDX]))

    def __is_valid_line(self, line: str) -> list:
        min_value_validator = MinValueValidator(0, message='value must be over 0')
        line.strip()
        if line is None or line == '':
            raise Exception("Incorrect line, please review file")
        values: list = line.split(self.SEPARATOR)
        if len(values) != 5:
            raise Exception("Incorrect line, please review file")
        cost: int = int(values[self.COST_IDX])
        quantity: int = int(values[self.QUANTITY_IDX])
        min_value_validator(cost)
        min_value_validator(quantity)
        return values
