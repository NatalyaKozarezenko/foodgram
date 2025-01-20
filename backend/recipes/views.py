"""RecipeDetailView - Ссылка на рецепт."""

from api.serializers import RecipeReadSerializer
from recipes.models import Recipe
from rest_framework.views import APIView


class RecipeDetailView(APIView):
    """Ссылка на рецепт."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
