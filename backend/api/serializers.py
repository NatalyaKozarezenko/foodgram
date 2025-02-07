"""Проверка и преобразование."""

from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.constants import MIN_AMOUNT
from recipes.models import DBUser, Ingredient, Recipe, RecipeIngredient, Tag
from recipes.validators import validate_username


class IngredientSerializer(serializers.ModelSerializer):
    """Отображение ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Отображение тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class UsersSerializer(DjoserUserSerializer):
    """Отображение пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = DBUser
        fields = (*DjoserUserSerializer.Meta.fields, 'is_subscribed', 'avatar')

    def validate_username(self, username):
        """Проверка имени пользователя."""
        return validate_username(username)

    def get_is_subscribed(self, user):
        """Получение подписок пользователя."""
        request = self.context.get('request', None)
        return (
            request is not None and request.user.is_authenticated
            and request.user.subscribers.filter(author=user).exists()
        )


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Промежуточная таблица рецептов и ингредиентов."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient
        read_only_fields = fields


class RecipeReadSerializer(serializers.ModelSerializer):
    """Отображение рецептов."""

    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipeingredients',
        many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    author = UsersSerializer()

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        model = Recipe
        read_only_fields = fields

    def get_filter(self, obj):
        """Поиск наличия записи."""
        request = self.context.get('request', None)
        return (
            request is not None and request.user.is_authenticated
            and obj.filter(user=request.user).exists()
        )

    def get_is_favorited(self, obj):
        """Проверка наличия в избранном."""
        return self.get_filter(obj.is_favorited)

    def get_is_in_shopping_cart(self, obj):
        """Проверка наличия в списке покупок."""
        return self.get_filter(obj.is_in_shopping_cart)


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Для сохранения ингредиентов рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(min_value=MIN_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сохранение рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )
    ingredients = RecipeIngredientCreateSerializer(many=True, required=True)
    image = Base64ImageField(use_url=True, required=True)
    cooking_time = serializers.IntegerField(min_value=MIN_AMOUNT)

    class Meta:
        fields = '__all__'
        model = Recipe

    def validate_image(self, image):
        """Проверка что поле не пустое."""
        if not image:
            raise serializers.ValidationError('Добавьте фотографию рецепта.')
        return image

    def find_double(self, ids):
        """Проверка на дубли."""
        double = set(
            element.id for element in ids if ids.count(element) >= 2
        )
        if double:
            raise serializers.ValidationError(
                f'Есть дубли: {double}.'
            )
        return ids

    def validate_tags(self, tags):
        """Проверка на дубли тегов."""
        return self.find_double(tags)

    def validate_ingredients(self, ingredients_amounts):
        """Проверка на дубли ингредиентов."""
        self.find_double([
            ingredient_amont['id'] for ingredient_amont in ingredients_amounts
        ])
        return ingredients_amounts

    def validate(self, recipe):
        """Проверка на заполненость ингредиентов и тегов."""
        if not recipe.get('ingredients'):
            raise serializers.ValidationError(
                'Добавьте хотя бы 1 ингредиент.'
            )
        if not recipe.get('tags'):
            raise serializers.ValidationError(
                'Добавьте хотя бы 1 тег.'
            )
        return recipe

    def save_recipes(self, recipe, ingredients):
        """Запись данных."""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ing['id'],
                amount=ing['amount']
            ) for ing in ingredients
        )

    def create(self, validated_data):
        """Сохранение рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        print(tags)
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.save_recipes(recipe, ingredients)
        print(recipe)
        return recipe

    def update(self, instance, validated_data):
        """Изменение рецепта."""
        instance.tags.set(validated_data.pop('tags'))
        instance.ingredients.clear()
        self.save_recipes(instance, validated_data.pop('ingredients'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Отображение рецепта с полными данными."""
        return RecipeReadSerializer(
            context=self.context).to_representation(instance)


class MinRecipeSerializer(serializers.ModelSerializer):
    """Отображение рецепта с минимальными данными."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class UsersSubscriptionsSerializer(UsersSerializer):
    """Пользователи с рецептами, на которых подписались."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta(UsersSerializer.Meta):
        fields = (*UsersSerializer.Meta.fields, 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Выводим репецпы на кого подписались."""
        return MinRecipeSerializer(
            obj.recipes.all()[:int(
                self.context.get('request').GET.get('recipes_limit', 10**10)
            )],
            many=True,
            context=self.context
        ).data


class AvatarSerializer(serializers.ModelSerializer):
    """Аватар."""

    avatar = Base64ImageField(use_url=True, required=True)

    class Meta:
        """Мета данных аватара."""

        model = DBUser
        fields = ('avatar',)
