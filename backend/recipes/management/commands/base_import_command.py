"""Базовый класс для импорта json-данных."""

import json

from django.core.management.base import BaseCommand

from foodgram_backend.settings import PATH_FOR_CSV
from recipes.models import Ingredient


class Import(BaseCommand):
    """Загрузка json-данных."""

    help = 'Загрузка json-данных.'
    filename = 'filename.json'
    model = Ingredient

    def handle(self, *args, **options):
        """Загрузка данных."""
        filename = PATH_FOR_CSV + self.filename
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data_import = self.model.objects.bulk_create(
                    (self.model(**data) for data in json.load(f)),
                    # Лишнее создание списка. Удалите квадратные скобки.
                    ignore_conflicts=True
                )
            self.stdout.write(
                f'Из файла {self.filename} загружено '
                f'{len(data_import)} записей.'
            )
        except Exception as error:
            self.stdout.write(f'Ошибка: {error} при импорте {self.filename}.')
