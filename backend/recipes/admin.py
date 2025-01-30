"""Настройка админки."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Max, Min
from django.utils.safestring import mark_safe

from recipes.models import (DBUser, Favorites, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Subscriptions, Tag)

admin.site.empty_value_display = 'Не задано'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Продукты."""

    list_display = (
        'name', 'measurement_unit', 'get_count_ingredient_in_recipes'
    )
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description='Количество рецептов')
    def get_count_ingredient_in_recipes(self, ingredient):
        """Количество рецептов с данным ингредиентом."""
        return ingredient.RecipeIngredient.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Теги."""

    list_display = ('name', 'slug', 'get_count_tag_in_recipes')
    search_fields = ('name', 'slug')

    @admin.display(description='Количество рецептов')
    def get_count_tag_in_recipes(self, tag):
        """Количество рецептов с данным тегом."""
        return tag.recipes.count()


class CookingTimeFilter(admin.SimpleListFilter):
    """Фильтр по времени готовки."""

    title = 'Время готовки'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        """Параметры фильтра."""
        cooking_times = model_admin.model.objects.aggregate(
            Min('cooking_time'), Max('cooking_time')
        )
        min_cooking_time = cooking_times['cooking_time__min']
        max_cooking_time = cooking_times['cooking_time__max']
        delta = (max_cooking_time - min_cooking_time) // 3
        self.quickly_time = min_cooking_time + delta
        self.long_time = max_cooking_time - delta
        quickly_count = model_admin.model.objects.filter(
            cooking_time__lt=self.quickly_time).count()
        medium_count = model_admin.model.objects.filter(
            cooking_time__gt=self.quickly_time,
            cooking_time__lt=self.long_time).count()
        long_count = model_admin.model.objects.filter(
            cooking_time__gt=self.long_time).count()
        return [
            ('quickly', f'Быстрее {self.quickly_time} мин ({quickly_count})'),
            ('medium', f'Быстрее {self.long_time} мин ({medium_count})'),
            ('long', f'Долго ({long_count})'),
        ]

    def queryset(self, request, queryset):
        """Проверка наличия подписчиков."""
        if self.value() == 'quickly':
            return queryset.filter(cooking_time__lt=self.quickly_time)
        elif self.value() == 'medium':
            return queryset.filter(
                cooking_time__gt=self.quickly_time,
                cooking_time__lt=self.long_time
            )
        elif self.value() == 'long':
            return queryset.filter(cooking_time__gt=self.long_time)
        return queryset


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Рецепты."""

    list_display = (
        'id', 'name', 'author', 'cooking_time', 'get_favorited_count',
        'get_tag', 'get_ingredients', 'get_image'
    )
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('tags', CookingTimeFilter, 'author')
    list_display_links = ('name',)
    filter_horizontal = ('tags',)

    @admin.display(description='Тег(и)')
    def get_tag(self, recipe):
        """Отображение тегов рецепта."""
        return '\n '.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='В избранном')
    def get_favorited_count(self, recipe):
        """Общее кол-во пользователей, у кого рецепт в избранном."""
        return recipe.is_favorited.count()

    @admin.display(description='Продукт(ы)')
    def get_ingredients(self, recipe):
        """Продукты в рецепте."""
        return '\n'.join(
            ingredients.name for ingredients in recipe.ingredients.all()
        )

    @admin.display(description='Изображение')
    @mark_safe
    def get_image(self, user):
        """Изображение рецепта."""
        if user.image and user.image.url:
            return f'<img src="{user.image.url}" style="max-height: 20px;">'
        return None


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Продукты и мера в рецепте."""

    list_display = ('recipe', 'ingredient', 'amount')


class BaseFilter(admin.SimpleListFilter):
    """Базовый фильтр."""

    title = 'Базовый фильтр'
    parameter_name = ''
    filter_fields = [
        ('True', 'Есть рецепты'),
        ('False', 'Нет рецептов'),
    ]
    queryset_params = {
        'True': {'recipes__isnull': False},
        'False': {'recipes__isnull': True},
    }

    def lookups(self, request, model_admin):
        """Параметры фильтра."""
        return self.filter_fields

    def queryset(self, request, queryset):
        """Запросы фильтра."""
        filter_params = self.queryset_params.get(self.value(), {})
        if filter_params:
            return queryset.filter(**filter_params).distinct()
        return queryset


class RecipesFilter(BaseFilter):
    """Фильтр по наличию рецептов."""

    title = 'Рецепты'
    parameter_name = 'get_recipes_count'


class SubscribersFilter(BaseFilter):
    """Фильтр по наличию подписчиков."""

    title = 'Подписчики'
    parameter_name = 'get_subscribers_count'
    filter_fields = [
        ('True', 'Есть подписчики'),
        ('False', 'Нет подписчиков'),
    ]
    queryset_params = {
        'True': {'authors__isnull': False},
        'False': {'authors__isnull': True},
    }


class SubscriptionsFilter(BaseFilter):
    """Фильтр по наличию подписки."""

    title = 'Подписки'
    parameter_name = 'get_subscriptions_count'
    filter_fields = [
        ('True', 'Есть подписки'),
        ('False', 'Нет подписок'),
    ]
    queryset_params = {
        'True': {'subscribers__isnull': False},
        'False': {'subscribers__isnull': True},
    }


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
        return ''

    @admin.display(description='Рецепты')
    def get_recipes_count(self, user):
        """Количество рецептов пользователя."""
        return user.recipes.count()

    @admin.display(description='Количество подписок')
    def get_subscriptions_count(self, user):
        """Количество подписок."""
        return user.subscribers.count()

    @admin.display(description='Количество подписчиков')
    def get_subscribers_count(self, user):
        """Количество подписчиков."""
        return user.authors.count()


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    """Подписки."""

    list_display = ('subscriber', 'author')
    search_fields = ('subscriber', 'author')


@admin.register(Favorites, ShoppingCart)
class DefaultAdmin(admin.ModelAdmin):
    """Избранное и Список покупок."""

    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
