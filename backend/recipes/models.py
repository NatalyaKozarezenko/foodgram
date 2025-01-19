from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse_lazy

from recipes.constants import (
    MAX_LEN_MEASUREMENT_UNIT, MAX_LEN_NAME_INGREDIENT, MAX_LEN_TAG,
    MAX_LEN_TEXT, MESSAGE, MIN_VALUE, LOOK_TEXT
)
from users.models import DBUser


def min_value(value):
    if value < MIN_VALUE:
        raise ValidationError(f'{MESSAGE}')
    return value


class Tag(models.Model):
    name = models.CharField('Название', max_length=MAX_LEN_TAG, unique=True)
    slug = models.SlugField('Слаг', max_length=MAX_LEN_TAG, unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=MAX_LEN_NAME_INGREDIENT)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LEN_MEASUREMENT_UNIT
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:LOOK_TEXT]


class Recipe(models.Model):
    name = models.CharField('Название', max_length=MAX_LEN_TEXT)
    text = models.TextField('Описание', blank=True, null=True)
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[min_value]
    )
    image = models.ImageField(upload_to='recipes/images/')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        DBUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        blank=True
    )
    is_favorited = models.ManyToManyField(
        DBUser,
        verbose_name='Избранное',
        related_name='favorited',
        blank=True
    )
    is_in_shopping_cart = models.ManyToManyField(
        DBUser,
        verbose_name='Список покупок',
        related_name='shopping_carts',
        related_query_name='shopping_cart',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name[:LOOK_TEXT]

    def get_tag(self):
        return Tag.objects.filter(recipes=self)

    def get_absolute_url(self):
        return reverse_lazy('recipes-detail', args=[self.id])

    def get_favorited_count(self):
        return self.is_favorited.count()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[min_value]
    )

    def __str__(self):
        return f'{self.recipe} {self.amount} {self.ingredient}'
