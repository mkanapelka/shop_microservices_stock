from django.db import models
from stock.models import Base


class Characteristic(Base):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "characteristic"

    def __str__(self):
        return self.name
