from django.core.management.base import BaseCommand
import json

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Загрузка json-данных в модель Ингрединеты.'

    def handle(self, *args, **options):
        filename = 'data/tags.json'
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for concert in data:
                Tag.objects.create(**concert)
            self.stdout.write(f'Загрузка {filename} завершена.')
        except FileNotFoundError:
            self.stdout.write('Файл {filename} не найден!')
