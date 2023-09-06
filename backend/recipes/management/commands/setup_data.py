import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загуржает ингредиенты в базу данных'

    def handle(self, *args, **kwargs):
        with open('../data/ingredients.json', 'r') as f:
            data = json.load(f)
            try:
                Ingredient.objects.bulk_create([
                    Ingredient(**row) for row in data
                ])
            except Exception as e:
                print('Произошла ошибка:', e)
