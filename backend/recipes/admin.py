"""Настройка админки."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Max, Min
from django.utils.safestring import mark_safe

from recipes.models import (DBUser, Favorites, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Subscriptions, Tag)

admin.site.empty_value_display = 'Не задано'

admin.site.unregister(Group)


class CountRecipesMixin:
    """Миксин счёта рецептов."""

    @admin.display(description='Рецепты')
    def get_count_in_recipes(self, obj):
        """Количество рецептов."""
        return obj.recipes.count()


@admin.register(Ingredient)
class IngredientAdmin(CountRecipesMixin, admin.ModelAdmin):
    """Продукты."""

    list_display = (
        'name', 'measurement_unit', 'get_count_in_recipes'
    )
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(CountRecipesMixin, admin.ModelAdmin):
    """Теги."""

    list_display = ('name', 'slug', 'get_count_in_recipes')
    search_fields = ('name', 'slug')


class CookingTimeFilter(admin.SimpleListFilter):
    """Фильтр по времени готовки."""

    title = 'Время готовки'
    parameter_name = 'cooking_time'

    def get_recipes(self, period_key, recipes=None):
        """Объекты за период."""
        if recipes is None:
            recipes = self.recipes
        return recipes.filter(
            cooking_time__range=self.periods.get(period_key)
        )

    def lookups(self, request, model_admin):
        """Параметры фильтра."""
        cooking_times = model_admin.model.objects.aggregate(
            Min('cooking_time'), Max('cooking_time')
        )
        min_cooking_time = cooking_times['cooking_time__min']
        max_cooking_time = cooking_times['cooking_time__max']
        if min_cooking_time == max_cooking_time:
            return []
        delta = (max_cooking_time - min_cooking_time) // 3
        quickly_time = min_cooking_time + delta
        long_time = max_cooking_time - delta
        self.periods = {
            'quickly': (0, quickly_time),
            'medium': (quickly_time + 1, long_time),
            'long': (long_time + 1, 10**10),
        }
        self.recipes = model_admin.model.objects
        count_quickly_recipes = self.get_recipes('quickly').count()
        count_medium_recipes = self.get_recipes('medium').count()
        count_long_recipes = self.get_recipes('long').count()
        return [
            ('quickly',
             f'Быстрее {quickly_time} мин ({count_quickly_recipes})'),
            ('medium', f'Быстрее {long_time} мин ({count_medium_recipes})'),
            ('long', f'Долго ({count_long_recipes})'),
        ]

    def queryset(self, request, recipes):
        """Рецепты по времени готовки."""
        params = self.value()
        if params:
            return self.get_recipes(params, recipes)
        return recipes


class RecipeIngredientInline(admin.TabularInline):
    """Продукты при редактировании рецепта."""

    model = RecipeIngredient
    extra = 1
    min_num = 1


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
    inlines = (RecipeIngredientInline,)

    @admin.display(description='Тег(и)')
    @mark_safe
    def get_tag(self, recipe):
        """Отображение тегов рецепта."""
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='В избранном')
    def get_favorited_count(self, recipe):
        """Количество добавления рецепта в избранне."""
        return recipe.is_favorited.count()

    @admin.display(description='Продукт(ы)')
    @mark_safe
    def get_ingredients(self, recipes):
        """Продукты в рецепте."""
        return '<br>'.join('{}: {} ({})'.format(
            recipe.ingredient.name,
            recipe.amount,
            recipe.ingredient.measurement_unit
        ) for recipe in recipes.recipeingredients.all()
        )

    @admin.display(description='Изображение')
    @mark_safe
    def get_image(self, recipe):
        """Изображение рецепта."""
        if recipe.image and recipe.image.url:
            return f'<img src="{recipe.image.url}" style="max-height: 80px;">'
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
        ('True', 'Есть данные'),
        ('False', 'Нет данных'),
    ]
    queryset_params = {
        'True': {'data__isnull': False},
        'False': {'data__isnull': True},
    }

    def lookups(self, request, model_admin):
        """Параметры фильтра."""
        return self.filter_fields

    def queryset(self, request, queryset):
        """Запросы фильтра."""
        filter_params = self.queryset_params.get(self.value())
        if filter_params:
            return queryset.filter(**filter_params).distinct()
        return queryset


class RecipesFilter(BaseFilter):
    """Фильтр по наличию рецептов."""

    title = 'Рецепты'
    parameter_name = 'get_recipes_count'
    filter_fields = [
        ('True', 'Есть рецепты'),
        ('False', 'Нет рецептов'),
    ]
    queryset_params = {
        'True': {'recipes__isnull': False},
        'False': {'recipes__isnull': True},
    }


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
class UserAdmin(CountRecipesMixin, BaseUserAdmin):
    """Пользователи."""

    fieldsets = (
        (None, {'fields': ('email', 'password', 'avatar')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions'
        )}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = (
        'id', 'username', 'get_fio', 'email', 'get_avatar',
        'get_count_in_recipes', 'get_subscriptions_count',
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
            return f'<img src="{user.avatar.url}" style="max-height: 80px;">'
        return None

    @admin.display(description='Подписки')
    def get_subscriptions_count(self, user):
        """Количество подписок."""
        return user.subscribers.count()

    @admin.display(description='Подписчиков')
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
