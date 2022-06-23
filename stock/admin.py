from django.contrib import admin

from stock.models import Product, Characteristic, Category

admin.site.regicter(Product)
admin.site.regicter(Category)
admin.site.regicter(Characteristic)
