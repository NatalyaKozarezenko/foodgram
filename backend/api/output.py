"""Формирование тела СпискаПокупок."""


def get_output(recipes, ingredients_info, current_date):
    """Формирование тела СпискаПокупок."""
    return '\n'.join(
        [f'Список покупок от {current_date.strftime("%d.%m.%Y")}',
         'Мера (ед.изм.) и название:']
        + [f'{i}) {ingredient_info["total_amount"]}'
           f'({ingredient_info["ingredient__measurement_unit"]}) - '
            f'{ingredient_info["ingredient__name"].capitalize()}'
           for i, ingredient_info in enumerate(ingredients_info, 1)]
        + ['Перечень рецептов:']
        + [f'{i}) {recipe["name"]}'
           f'({recipe["author__first_name"][0].capitalize()}'
           f'.{recipe["author__last_name"].capitalize()})'
           for i, recipe in enumerate(recipes, 1)]
    )
