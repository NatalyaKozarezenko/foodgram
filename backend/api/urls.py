from django.urls import include, path
from rest_framework import routers

from api.views import (
    AvatarViewSet,
    CostomsViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet
)


router_v1 = routers.DefaultRouter()
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('users', CostomsViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('users/me/avatar/', AvatarViewSet.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
]
