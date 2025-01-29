"""Загрузка json-данных в модель Теги."""

import json

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    """Загрузка json-данных в модель Теги."""

    help = 'Загрузка json-данных в модель Теги.'

    def handle(self, *args, **options):
        """Загрузка данных."""
        filename = 'data/tags.json'
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for concert in data:
                Tag.objects.create(**concert)
            self.stdout.write(f'Загрузка {filename} завершена.')
        except FileNotFoundError:
            self.stdout.write('Файл {filename} не найден!')
