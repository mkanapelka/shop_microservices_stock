from django.db import models
from stock.models import Base


class Category(Base):
    name = models.CharField(max_length=255, unique=True, db_index=True)

    class Meta:
        db_table = "category"
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
