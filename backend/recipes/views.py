"""RecipeDetailView - Ссылка на рецепт."""

from django.shortcuts import redirect

from recipes.models import Recipe


def redirect_view(request, id):
    """переадресация с короткой ссылки."""
    _ = Recipe.objects.get(pk=id)
    return redirect(request.build_absolute_uri(f'/recipes/{id}/'))
