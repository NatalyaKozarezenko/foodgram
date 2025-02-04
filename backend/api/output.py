"""Формирование тела СпискаПокупок."""

def get_output(recipes, ingredients_info, current_date):
    """Формирование тела СпискаПокупок."""
    return '\n'.join([
        'Список покупок от {}г.'.format(current_date),
        'Мера (ед.изм.) и название:',
        *['{}) {} ({}) - {}'.format(
            i, 
            ingredient_info["total_amount"], 
            ingredient_info["ingredient__measurement_unit"], 
            ingredient_info["ingredient__name"].capitalize())
       for i, ingredient_info in enumerate(ingredients_info, 1)],
# Разместите заготовку за пределами функции.
        'Перечень рецептов:',
        *['{}) {} ({})'.format(
            i, 
            recipe["name"],
            recipe["author__username"])
       for i, recipe in enumerate(recipes, 1)],
    ])

# Разместите заготовку за пределами функции.