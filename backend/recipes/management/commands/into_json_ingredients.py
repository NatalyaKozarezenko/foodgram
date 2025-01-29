"""Загрузка json-данных в модель Ингрединеты."""

from django.core.management.base import BaseCommand
import json

from foodgram_backend.settings import PATH_FOR_CSV
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка json-данных в модель Ингрединеты.'

    def handle(self, *args, **options):
        filename = PATH_FOR_CSV + 'ingredients.json'
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for concert in data:
                Ingredient.objects.create(**concert)
            self.stdout.write(f'Загрузка {filename} завершена.')
        except FileNotFoundError:
            self.stdout.write('Файл {filename} не найден!')
