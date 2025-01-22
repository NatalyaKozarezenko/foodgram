import django_filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(django_filters.FilterSet):
    """Фильтр по данным рецепта."""

    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        distinct=True
    )
    is_favorited = django_filters.ChoiceFilter(
        choices=[(1, 'True'), (0, 'False')],
        method='is_favorited_filter'
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=[(1, 'True'), (0, 'False')],
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        """Мета класс фильтра рецепта."""

        model = Recipe
        fields = ('tags', 'is_favorited', 'author', 'is_in_shopping_cart')

    def is_favorited_filter(self, queryset, name, value):
        """Проверка рецепта в избранном."""
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if value else queryset
        if int(value) == 1:
            return queryset.filter(is_favorited=user)
        elif int(value) == 0:
            return queryset.exclude(is_favorited=user)
        else:
            return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        """Проверка рецепта в списке покупок."""
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if value else queryset
        if int(value) == 1:
            return queryset.filter(is_in_shopping_cart=user)
        elif int(value) == 0:
            return queryset.exclude(is_in_shopping_cart=user)
        else:
            return queryset


class IngredientFilter(django_filters.FilterSet):
    """Фильтр по начальным значением ингредиента."""

    name = django_filters.CharFilter(
        field_name='name', lookup_expr='istartswith'
    )

    class Meta:
        """Мета класс фильтра ингредиентов."""

        model = Ingredient
        fields = ['name']
