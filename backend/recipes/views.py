"""RecipeDetailView - Ссылка на рецепт."""

from django.shortcuts import get_object_or_404, redirect

from recipes.models import Recipe


def redirect_view(request, id):
    recipe = get_object_or_404(Recipe, pk=id)
    # получаем url из get_absolute_url в модели
    return redirect(recipe)
