"""
Загрузка данных.

Файлы Тегов и Ингридиентов должны размещаться в директории PATH_FOR_CSV
в корне проекта.
"""

import csv
import glob
import os

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.http.response import Http404

from foodgram_backend.settings import PATH_FOR_CSV
from recipes.models import Ingredient, Tag

MODELS_DICT = {
    'ingredients': Ingredient,
    'tags': Tag,
}


class Command(BaseCommand):
    """Поиск файлов, моделей и загрузка данных."""

    help = 'Импорт информации из CSV-файла.'

    def load_file(self, path):
        """Поиск файлов."""
        path += '*.csv'
        files = []
        for filename in glob.glob(os.path.join(path)):
            files.append(filename)
        return files

    def get_model(self, filename):
        """Поиск моделей."""
        for file in MODELS_DICT:
            if file in filename:
                return MODELS_DICT[file]

    def handle(self, *args, **kwargs):
        """Загрузка данных."""
        files = self.load_file(PATH_FOR_CSV)

        for filename in files:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    model = self.get_model(filename)
                    data = []

                    try:
                        if model:
                            for row in csv_reader:
                                data.append(model(**row))
                        else:
                            self.stdout.write(
                                f'Не найдена модель для {filename}!')

                        model.objects.bulk_create(data, ignore_conflicts=True)
                        self.stdout.write(f'Загрузка {filename} завершена.')
                    except Http404:
                        files.append(filename)
                    except IntegrityError:
                        files.append(filename)
            except FileNotFoundError:
                self.stdout.write('Файл не найден!')
        self.stdout.write('Загрузка закончена.')
