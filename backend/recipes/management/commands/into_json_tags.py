"""Загрузка json-данных в модель Теги."""

from recipes.management.commands.into_json_ingredients import Import
from recipes.models import Tag


class Command(Import):
    """Загрузка json-данных в модель Теги."""

    help = 'Загрузка json-данных в модель Теги.'

    def handle(self, *args, **options):
        """Загрузка данных."""
        filename = 'data/tags.json'
        super().handle(filename, model=Tag)
