"""RecipeDetailView - Ссылка на рецепт."""

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect

from recipes.models import Recipe


def redirect_view(request, id):
    """переадресация с короткой ссылки."""
    recipe = get_object_or_404(Recipe, pk=id)
    return redirect(f'{settings.HOST}/recipes/{recipe.id}/')
