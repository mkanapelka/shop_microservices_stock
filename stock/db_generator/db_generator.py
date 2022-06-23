from random import Random
from stock.models import Category, Characteristic, Product
from stock.db_generator.constans import Constants


class DbGeneratorService:

    @staticmethod
    def read_words_from_file(path: str) -> list:
        with open(path, 'r', encoding="utf8") as file:
            return file.readlines()

    @staticmethod
    def put_categories() -> list:
        category_names = DbGeneratorService.read_words_from_file(Constants.PATH_TO_CATEGORY_NAMES)
        categories = list(map(lambda it: Category(name=it), category_names))
        for category in categories:
            category.save()
        return categories

    @staticmethod
    def put_characteristics() -> list:
        characteristic_name = DbGeneratorService.read_words_from_file(Constants.PATH_TO_CHARACTERISTIC_NAMES)
        characteristics = list(map(lambda it: Characteristic(name=it), characteristic_name))
        for characteristic in characteristics:
            characteristic.save()
        return characteristics

    @staticmethod
    def get_random_value_from_list(lst: list, random: Random):
        return lst[random.randint(0, len(lst) - 1)]

    @staticmethod
    def create_product(categories: list,
                       characteristics: list,
                       adjectives: list,
                       nouns: list,
                       random: Random) -> Product.objects:

        cost = random.randint(Constants.MIN_COST, Constants.MAX_COST)
        quantity = random.randint(0, Constants.MAX_QUANTITY)
        category = DbGeneratorService.get_random_value_from_list(categories, random)
        name = DbGeneratorService.get_random_value_from_list(adjectives, random) + " " + DbGeneratorService.get_random_value_from_list(nouns, random)
        product = Product.objects.create(name=name, cost=cost, quantity=quantity, category=category,
                                         status=Product.ProductStatus.AVAILABLE)
        product.characteristic.add(DbGeneratorService.get_random_value_from_list(characteristics, random),
                                   DbGeneratorService.get_random_value_from_list(characteristics, random))
        return product

    @staticmethod
    def put_products() -> None:
        adjectives = DbGeneratorService.read_words_from_file(Constants.PATH_TO_ADJECTIVES)
        nouns = DbGeneratorService.read_words_from_file(Constants.PATH_TO_NOUNS)

        categories = Category.objects.all()
        characteristics = Characteristic.objects.all()

        random = Random()

        for i in range(0, Constants.QUANTITY_PRODUCT):
            DbGeneratorService.create_product(categories, characteristics, adjectives, nouns, random)
