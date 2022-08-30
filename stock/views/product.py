from django.db import transaction
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from stock.models import Product
from stock.serializers.product import ProductSerializer
from stock.service.product import ProductServiceImpl


class ProductApiViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (JSONParser,)
    product_service = ProductServiceImpl()

    def filter_queryset(self, queryset):
        queryset = Product.objects.all()
        return self.product_service.get_dynamic_queryset(self.request, queryset)

    @transaction.atomic(durable=True)
    @action(methods=['patch'], detail=True)
    def update_quantity(self, request, *args, **kwargs):
        product: Product = self.product_service.update_quantity(request, *args, **kwargs)
        return Response(product)


class ProductAdminApiViewSet(GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser,)
    product_service = ProductServiceImpl()

    @transaction.atomic(durable=True)
    @action(methods=['put'], url_path='upload', detail=True)
    def add_products_from_file(self, request, *args, **kwargs):
        products = self.product_service.add_products_from_file(self, request, *args, **kwargs)
        for product in products:
            serializer = ProductSerializer(data=product.__dict__)
            serializer.is_valid(raise_exception=True)
            serializer.save(category_id=product.category_id)
        return Response(status=status.HTTP_200_OK)
