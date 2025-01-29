"""
Настройка админки.

IngredientAdmin - Продукты.
TagAdmin - Теги.
RecipeAdmin - Рецепты.
UserAdmin - Пользователи.
SubscriptionsAdmin - Подписки.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe

from recipes.models import (DBUser, Favorites, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Subscriptions, Tag)

admin.site.empty_value_display = 'Не задано'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Продукты."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Теги."""

    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Рецепты."""

    list_display = ('name', 'author', 'get_favorited_count', 'get_tag')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    list_display_links = ('name',)
    filter_horizontal = ('tags',)

    @admin.display(description='Тег(и)')
    def get_tag(self, recipe):
        """Отображение тегов рецепта."""
        return ', '.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Общее кол-во в избранном')
    def get_favorited_count(self, recipe):
        """Общее кол-во пользователей, у кого рецепт в избранном."""
        return Favorites.objects.filter(recipe=recipe).count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Продукты и мера в рецепте."""

    list_display = ('recipe', 'ingredient', 'amount')


class RecipesFilter(admin.SimpleListFilter):
    """Фильтр по наличию рецептов."""

    title = 'Рецепты'
    parameter_name = 'get_recipes_count'

    def lookups(self, request, model_admin):
        """Параметры фильтра."""
        return [
            ('True', 'Есть рецепты'),
            ('False', 'Нет рецептов'),
        ]

    def queryset(self, request, queryset):
        """Проверка наличия рецептов."""
        if self.value() == 'True':
            return queryset.filter(recipes__isnull=False).distinct()
        elif self.value() == 'False':
            return queryset.filter(recipes__isnull=True)


class SubscribersFilter(admin.SimpleListFilter):
    """Фильтр по наличию подписчиков."""

    title = 'Подписчики'
    parameter_name = 'get_subscribers_count'

    def lookups(self, request, model_admin):
        """Параметры фильтра."""
        return [
            ('True', 'Есть подписчики'),
            ('False', 'Нет подписчиков'),
        ]

    def queryset(self, request, queryset):
        """Проверка наличия подписчиков."""
        if self.value() == 'True':
            return queryset.filter(authors__isnull=False).distinct()
        elif self.value() == 'False':
            return queryset.filter(authors__isnull=True)


class SubscriptionsFilter(admin.SimpleListFilter):
    """Фильтр по наличию подписки."""

    title = 'Подписки'
    parameter_name = 'get_subscriptions_count'

    def lookups(self, request, model_admin):
        """Параметры фильтра."""
        return [
            ('True', 'Есть подписки'),
            ('False', 'Нет подписок'),
        ]

    def queryset(self, request, queryset):
        """Проверка наличия подписок."""
        if self.value() == 'True':
            return queryset.filter(subscribers__isnull=False).distinct()
        elif self.value() == 'False':
            return queryset.filter(subscribers__isnull=True)


@admin.register(DBUser)
class UserAdmin(BaseUserAdmin):
    """Пользователи."""

    list_display = (
        'id', 'username', 'get_fio', 'email', 'get_avatar',
        'get_recipes_count', 'get_subscriptions_count',
        'get_subscribers_count'
    )
    list_display_links = ('email', 'username')
    list_filter = (SubscribersFilter, SubscriptionsFilter, RecipesFilter)
    search_fields = ('email', 'username')
    readonly_fields = ['get_avatar']

    @admin.display(description='ФИО')
    def get_fio(self, user):
        """ФИО пользователя."""
        return user.first_name + user.last_name

    @admin.display(description='Аватар')
    @mark_safe
    def get_avatar(self, user):
        """Аватар пользователя."""
        if user.avatar and user.avatar.url:
            return f'<img src="{user.avatar.url}" style="max-height: 20px;">'
        return None

    @admin.display(description='Количество рецептов')
    def get_recipes_count(self, user):
        """Количество рецептов пользователя."""
        return Recipe.objects.filter(author=user).count()

    @admin.display(description='Количество подписок')
    def get_subscriptions_count(self, user):
        """Количество подписок."""
        return Subscriptions.objects.filter(subscriber=user).count()

    @admin.display(description='Количество подписчиков')
    def get_subscribers_count(self, user):
        """Количество подписчиков."""
        return Subscriptions.objects.filter(author=user).count()


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    """Подписки."""

    list_display = ('subscriber', 'author')
    search_fields = ('subscriber', 'author')


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    """Избранное."""

    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Избранное."""

    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
