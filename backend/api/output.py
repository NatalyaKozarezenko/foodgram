"""Формирование тела СпискаПокупок."""

from datetime import date


def get_output(recipes, ingredients_info):
    """Формирование тела СпискаПокупок."""
    shopping_cart = {}
    for info in ingredients_info:
        key = (info['ingredient__name'] + ' ('
               + info['ingredient__measurement_unit'] + ') — ')
        if key in shopping_cart:
            shopping_cart[key] = str(int(shopping_cart[key]) + info['amount'])
        else:
            shopping_cart[key] = (str(info['amount']))
    current_date = date.today()
    ingredients = [
        f'{i}. {key.capitalize()}{value}' for i, (key, value) in enumerate(
            shopping_cart.items(), 1
        )
    ]
    title_report = 'Список покупок от ' + current_date.strftime('%d.%m.%Y')
    title_ingredients = 'Название ингредиента (ед.измерения) и мера:'
    title_recipe = 'Перечень рецептов:'
    number_recipe_names = [f'{i}. {name}' for i, name in enumerate(recipes, 1)]
    return '\n'.join(
        [title_report, title_ingredients]
        + ingredients
        + [title_recipe]
        + number_recipe_names
    )
