"""RecipeDetailView - Ссылка на рецепт."""

from django.http import Http404
from django.shortcuts import redirect

from recipes.models import Recipe


def redirect_view(request, id):
    """переадресация с короткой ссылки."""
    if not Recipe.objects.filter(pk=id).exists():
        raise Http404
    return redirect(f'/recipes/{id}')
