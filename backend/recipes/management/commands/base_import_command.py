"""Базовый класс для импорта json-данных."""

import json

from django.core.management.base import BaseCommand

from foodgram_backend.settings import PATH_FOR_CSV


class Import(BaseCommand):
    """Загрузка json-данных."""

    help = 'Загрузка json-данных'
    filename = 'filename.json'
    model = None

    def handle(self, *args, **options):
        """Загрузка данных."""
        try:
            with open(
                PATH_FOR_CSV + self.filename, 'r', encoding='utf-8'
            ) as f:
                data_import = self.model.objects.bulk_create(
                    (self.model(**data) for data in json.load(f)),
                    ignore_conflicts=True
                )
            self.stdout.write(
                f'Из файла {self.filename} загружено '
                f'{len(data_import)} записей.'
            )
        except Exception as error:
            self.stdout.write(f'Ошибка: {error} при импорте {self.filename}.')
