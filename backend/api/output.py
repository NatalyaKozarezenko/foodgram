"""Формирование тела СпискаПокупок."""

from datetime import date

from django.http import FileResponse


def get_output(recipes, shopping_cart):
    """Формирование тела СпискаПокупок."""
    current_date = date.today()
    ingredients = [
        f'{i+1}. {key.capitalize()}{value}' for i, (key, value) in enumerate(
            shopping_cart.items()
        )
    ]
    title_report = 'Список покупок от ' + current_date.strftime('%d.%m.%Y')
    title_ingredients = 'Название ингредиента (ед.измерения) и мера:'
    title_recipe = 'Перечень рецептов:'
    number_recipe_names = [f'{i+1}. {name}' for i, name in enumerate(recipes)]
    with open('output.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(
            [title_report, title_ingredients]
            + ingredients
            + [title_recipe]
            + number_recipe_names))
    return FileResponse(open('output.txt', 'rb'),
                        as_attachment=True,
                        content_type='text/plain'
                        )
