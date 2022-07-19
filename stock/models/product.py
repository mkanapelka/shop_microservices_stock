from django.core.validators import MinValueValidator
from django.db import models

from stock.models import Base, Category, Characteristic


class Product(Base):
    class ProductStatus(models.TextChoices):
        MODERATION = 'MODERATION'
        AVAILABLE = 'AVAILABLE'
        SOLD_OUT = 'SOLD_OUT'
        ON_HOLD = 'ON_HOLD'
        DELETED = 'DELETED'

    name = models.CharField(max_length=255, unique=True)
    cost = models.IntegerField(validators=[MinValueValidator(0)])
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    status = models.CharField(max_length=50,
                              choices=ProductStatus.choices,
                              default=ProductStatus.AVAILABLE)
    category = models.ForeignKey(Category,
                                 on_delete=models.PROTECT,
                                 verbose_name="category_id",
                                 db_index=True,
                                 related_name='product')
    characteristic = models.ManyToManyField(Characteristic,
                                            db_table="links_product_to_characteristic",
                                            related_name="+")

    class Meta:
        ordering = ["name"]
        db_table = "product"

    def __str__(self):
        return self.name
