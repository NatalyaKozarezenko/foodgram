"""Загрузка json-данных в модель Теги."""

from recipes.management.commands._private import Import
from recipes.models import Tag


class Command(Import):
    """Загрузка json-данных в модель Теги."""

    help = 'Загрузка json-данных в модель Теги.'
    filename = 'tags.json'
    model = Tag
