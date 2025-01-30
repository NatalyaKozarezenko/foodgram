"""Загрузка json-данных в модель Ингрединеты."""

import json

from django.core.management.base import BaseCommand

from foodgram_backend.settings import PATH_FOR_CSV
from recipes.models import Ingredient


class Import(BaseCommand):
    """Загрузка json-данных."""

    help = 'Загрузка json-данных.'

    def handle(self, filename, model, *args, **options):
        """Загрузка данных."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                count = model.objects.bulk_create(
                    [model(**concert) for concert in json.load(f)]
                )
            self.stdout.write(
                f'Загрузка {filename} завершена.'
                f'Загружено {len(count)} новых записей.'
            )
        except Exception as error:
            self.stdout.write(f'Ошибка: {str(error)}')


class Command(Import):
    """Загрузка json-данных в модель Ингрединеты."""

    help = 'Загрузка json-данных в модель Ингрединеты.'

    def handle(self, *args, **options):
        """Загрузка данных."""
        filename = PATH_FOR_CSV + 'ingredients.json'
        super().handle(filename, model=Ingredient)
