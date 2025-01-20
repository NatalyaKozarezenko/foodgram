"""
Настройка админки.

IngredientAdmin - Ингредиенты
TagAdmin - Теги
RecipeAdmin - Рецепты
"""

from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag

admin.site.empty_value_display = 'Не задано'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Ингредиенты."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Теги."""

    list_display = ('name', 'slug')
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    """Рецепты."""

    list_display = (
        'name', 'author', 'get_tag', 'get_favorited',
        'get_shopping_cart', 'get_favorited_count'
    )
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    list_display_links = ('name',)
    filter_horizontal = ('tags',)

    @admin.display(description='Тег(и)')
    def get_tag(self, recipe):
        """Отображение тегов рецепта."""
        return ', '.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Избранное')
    def get_favorited(self, recipe):
        """У кого в избранном."""
        return ', '.join(
            favorited.username for favorited in recipe.is_favorited.all()
        )

    @admin.display(description='В списке покупок')
    def get_shopping_cart(self, recipe):
        """У кого в списке покупок."""
        return ', '.join(
            shopping.username for shopping in recipe.is_in_shopping_cart.all()
        )

    @admin.display(description='Общее кол-во в избранном')
    def get_favorited_count(self, recipe):
        """Общее кол-во пользователей, у кого рецепт в избранном."""
        return recipe.get_favorited_count()


admin.site.register(Recipe, RecipeAdmin)
