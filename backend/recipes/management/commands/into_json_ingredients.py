"""Загрузка json-данных в модель Ингрединеты."""

from recipes.management.commands._private import Import
from recipes.models import Ingredient


class Command(Import):
    """Загрузка json-данных в модель Ингрединеты."""

    help = 'Загрузка json-данных в модель Ингрединеты.'
    filename = 'ingredients.json'
    model = Ingredient
