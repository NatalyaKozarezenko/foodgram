"""
Модели.

Ingredient- Продукты.
Tag - Теги.
Recipe - Рецепты.
RecipeIngredient - Корректировка связной таблицы рецептов и продуктов.
DBUser - Пользователи.
SubscriptionsAdmin - Подписки.
Favorites - Избранное.
ShoppingCart - Список покупок.
"""

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (EMAIL_MAX_LENGTH, LOOK_TEXT,
                               MAX_LEN_MEASUREMENT_UNIT,
                               MAX_LEN_NAME_INGREDIENT, MAX_LEN_TAG,
                               MAX_LEN_TEXT, MAX_LENGTH_FIRST_NAME,
                               MAX_LENGTH_LAST_NAME, MAX_LENGTH_USERNAME,
                               MIN_COOKING_TIME)
from recipes.validators import validate_username


class DBUser(AbstractUser):
    """Пользователи."""

    email = models.EmailField(
        'email',
        max_length=EMAIL_MAX_LENGTH,
        unique=True
    )
    username = models.CharField(
        'Никнейм',
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[validate_username]
    )
    first_name = models.CharField('Имя', max_length=MAX_LENGTH_FIRST_NAME)
    last_name = models.CharField('Фамилия', max_length=MAX_LENGTH_LAST_NAME)
    avatar = models.ImageField(upload_to='users/images/', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        """Мета данные пользователя."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        """Отображение имени пользователя."""
        return self.username


class Tag(models.Model):
    """Теги."""

    name = models.CharField('Название', max_length=MAX_LEN_TAG, unique=True)
    slug = models.SlugField('Слаг', max_length=MAX_LEN_TAG, unique=True)

    class Meta:
        """Мета класс Тегов."""

        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        """Отображение название тега."""
        return self.name


class Ingredient(models.Model):
    """Продукты."""

    name = models.CharField('Название', max_length=MAX_LEN_NAME_INGREDIENT)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LEN_MEASUREMENT_UNIT
    )

    class Meta:
        """Мета класс продуктов."""

        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit',
            ),
        )

    def __str__(self):
        """Отображение названия продукта."""
        return f'{self.name[:LOOK_TEXT]} ({self.measurement_unit})'


class Recipe(models.Model):
    """Рецепты."""

    name = models.CharField('Название', max_length=MAX_LEN_TEXT)
    text = models.TextField('Описание')
    cooking_time = models.IntegerField(
        'Время (мин)',
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Продукты',
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        DBUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        blank=True
    )

    class Meta:
        """Мета класс рецептов."""

        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        """Отображение название рецепта."""
        return self.name[:LOOK_TEXT]


class RecipeIngredient(models.Model):
    """Корректировка связной таблицы рецептов и продуктов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукты',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )

    class Meta:
        """Мета класс связной таблицы."""

        verbose_name = 'Продукт в рецепте'
        verbose_name_plural = 'Продукты в рецепте'
        default_related_name = 'recipeingredients'

    def __str__(self):
        """Отображение рецептов и продуктов и их мера."""
        return f'{self.recipe} {self.amount} {self.ingredient}'


class Favorites(models.Model):
    """Избранное."""

    user = models.ForeignKey(
        DBUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_favorited',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета класс избранное."""

        ordering = ('recipe', 'user')
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorites',
            )
        ]

    def __str__(self):
        """Отображение рецептов в избранном."""
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    """Список покупок."""

    user = models.ForeignKey(
        DBUser,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_in_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета класс списка покупок."""

        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('recipe', 'user')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart',
            )
        ]

    def __str__(self):
        """Отображение рецептов в списки покупок."""
        return (
            f'Рецепт {self.recipe} в списке покупок у {self.user}'
        )


class Subscriptions(models.Model):
    """Подписки."""

    subscriber = models.ForeignKey(
        DBUser,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscribers'
    )
    author = models.ForeignKey(
        DBUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='authors'
    )

    class Meta:
        """Мета данные подписок."""

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='unique_subscriber_author',
            ),
        )

    def __str__(self):
        """Отображение связи подписок."""
        return f'{self.subscriber} подписан на {self.author}'
