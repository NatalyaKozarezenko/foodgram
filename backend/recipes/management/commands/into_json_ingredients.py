"""Загрузка json-данных в модель Ингрединеты."""

from backend.recipes.management.commands.base_import_command import Import
from recipes.models import Ingredient


class Command(Import):
    """Загрузка json-данных в модель Ингрединеты."""

    help = 'Загрузка json-данных в модель Ингрединеты.'
    filename = 'ingredients.json'
    model = Ingredient
