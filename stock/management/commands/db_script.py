from django.core.management import BaseCommand

from stock.db_generator.db_generator import DbGeneratorService


class Command(BaseCommand):
    def handle(self, *args, **options):
        DbGeneratorService.put_categories()
        DbGeneratorService.put_characteristics()
        DbGeneratorService.put_products()