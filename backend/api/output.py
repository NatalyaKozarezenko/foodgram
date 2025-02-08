"""Формирование тела СпискаПокупок."""

from datetime import date

from babel.dates import format_date

TEMPLATE = {
    'ingredients': '{number}) {total_amount} ({measurement_unit}) - {name}',
    'recipe': '{number}) {name} ({author})'
}


def get_output(recipes, ingredients_info):
    """Формирование тела СпискаПокупок."""
    current_date = format_date(
        date.today(),
        format='d MMMM yyyy',
        locale='ru_RU'
    )
    return '\n'.join([
        'Список покупок от {}'.format(current_date),
        'Нужно купить:',
        *[TEMPLATE['ingredients'].format(
            number=i,
            total_amount=ingredient_info['total_amount'],
            measurement_unit=ingredient_info['ingredient__measurement_unit'],
            name=ingredient_info['ingredient__name'].capitalize())
            for i, ingredient_info in enumerate(ingredients_info, 1)],
        'Что бы приготовить:',
        *[TEMPLATE['recipe'].format(
            number=i,
            name=recipe['name'],
            author=recipe['author__username'])
            for i, recipe in enumerate(recipes, 1)],
    ])
