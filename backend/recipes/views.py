"""RecipeDetailView - Ссылка на рецепт."""

from rest_framework.views import APIView

from api.serializers import RecipeReadSerializer
from recipes.models import Recipe


class RecipeDetailView(APIView):
    """Ссылка на рецепт."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
