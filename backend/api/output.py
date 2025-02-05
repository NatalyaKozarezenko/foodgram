"""Формирование тела СпискаПокупок."""


def get_output(recipes, ingredients_info, current_date, template):
    """Формирование тела СпискаПокупок."""
    return '\n'.join([
        'Список покупок от {}г.'.format(current_date),
        'Мера (ед.изм.) и название:',
        *[template['ingredients'].format(
            number=i,
            total_amount=ingredient_info['total_amount'],
            measurement_unit=ingredient_info['ingredient__measurement_unit'],
            name=ingredient_info['ingredient__name'].capitalize())
            for i, ingredient_info in enumerate(ingredients_info, 1)],
        'Перечень рецептов:',
        *[template['recipe'].format(
            number=i,
            name=recipe['name'],
            author=recipe['author__username'])
            for i, recipe in enumerate(recipes, 1)],
    ])
