from rest_framework.views import APIView

from api.serializers import RecipeReadSerializer
from recipes.models import Recipe


class RecipeDetailView(APIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
