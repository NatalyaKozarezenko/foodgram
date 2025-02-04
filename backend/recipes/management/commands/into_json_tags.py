"""Загрузка json-данных в модель Теги."""

from backend.recipes.management.commands.base_import_command import Import
from recipes.models import Tag


class Command(Import):
    """Загрузка json-данных в модель Теги."""

    help = 'Загрузка json-данных в модель Теги.'
    filename = 'tags.json'
    model = Tag
