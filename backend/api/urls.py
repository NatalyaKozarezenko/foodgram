"""Url адреса приложения api."""

from django.urls import include, path
from rest_framework import routers

from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       UsersViewSet)

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
