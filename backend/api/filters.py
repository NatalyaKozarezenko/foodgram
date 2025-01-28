"""Фильтрация рецептов и продуктов."""

import django_filters

from recipes.models import DBUser, Ingredient, Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    """Фильтр по данным рецепта."""

    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = django_filters.ChoiceFilter(
        choices=[(1, 'True'), (0, 'False')],
        method='is_favorited_filter'
    )
    author = django_filters.ModelChoiceFilter(
        field_name='author', queryset=DBUser.objects.all()
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=[(1, 'True'), (0, 'False')],
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        """Мета класс фильтра рецепта."""

        model = Recipe
        fields = ('tags', 'is_favorited', 'author', 'is_in_shopping_cart')

    def is_favorited_filter(self, recipes, name, value):
        """Проверка рецепта в избранном."""
        user = self.request.user
        if not user.is_authenticated:
            return recipes.none() if value else recipes
        if int(value) == 1:
            return recipes.filter(is_favorited__user=user)
        elif int(value) == 0:
            return recipes.exclude(is_favorited__user=user)
        else:
            return recipes

    def is_in_shopping_cart_filter(self, recipes, name, value):
        """Проверка рецепта в списке покупок."""
        user = self.request.user
        if not user.is_authenticated:
            return recipes.none() if value else recipes
        if int(value) == 1:
            return recipes.filter(is_in_shopping_cart__user=user)
        elif int(value) == 0:
            return recipes.exclude(is_in_shopping_cart__user=user)
        else:
            return recipes


class IngredientFilter(django_filters.FilterSet):
    """Фильтр по начальным значением продукта."""

    name = django_filters.CharFilter(
        field_name='name', lookup_expr='istartswith'
    )

    class Meta:
        """Мета класс фильтра продуктов."""

        model = Ingredient
        fields = ['name']
