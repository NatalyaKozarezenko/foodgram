"""Загрузка json-данных в модель Ингрединеты."""

import json

from django.core.management.base import BaseCommand

from foodgram_backend.settings import PATH_FOR_CSV
from recipes.models import Ingredient


class Command(BaseCommand):
    """Загрузка json-данных в модель Ингрединеты."""

    help = 'Загрузка json-данных в модель Ингрединеты.'

    def handle(self, *args, **options):
        """Загрузка данных."""
        filename = PATH_FOR_CSV + 'ingredients.json'
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for concert in data:
                Ingredient.objects.create(**concert)
            self.stdout.write(f'Загрузка {filename} завершена.')
        except FileNotFoundError:
            self.stdout.write('Файл {filename} не найден!')
