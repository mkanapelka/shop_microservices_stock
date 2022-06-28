from django.contrib import admin

from stock.models import Product, Characteristic, Category

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Characteristic)
