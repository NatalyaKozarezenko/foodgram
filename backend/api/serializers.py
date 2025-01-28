"""??????."""

from django.conf import settings
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.constants import MIN_AMOUNT
from recipes.models import DBUser, Ingredient, Recipe, RecipeIngredient, Tag
from recipes.validators import validate_username


class IngredientSerializer(serializers.ModelSerializer):
    """Отображение ингредиентов."""

    class Meta:
        """мета класс ингредиентов."""

        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Отображение тегов."""

    class Meta:
        """мета класс тегов."""

        model = Tag
        fields = '__all__'


class UsersSerializer(DjoserUserSerializer):
    """Отображение пользователей."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        """мета класс пользователей."""

        model = DBUser
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def validate_username(self, username):
        """Проверка имени пользователя."""
        return validate_username(username)

    def get_is_subscribed(self, user):
        """Получение подписок пользователя."""
        request = self.context.get('request', None)
        if request is not None and request.user.is_authenticated:
            return request.user.subscribers.filter(author=user).exists()
        return False

    def get_avatar(self, user):
        """Получение аватара пользователя."""
        if user.avatar:
            return f'{settings.HOST}{user.avatar.url}'
        return None


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Промежуточная таблица рецептов и ингредиентов."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=MIN_AMOUNT)

    class Meta:
        """Мета класс для промежуточная таблица рецептов и ингредиентов."""

        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class RecipeReadSerializer(serializers.ModelSerializer):
    """Отображение рецептов."""

    tags = TagSerializer(many=True)
    # image = serializers.SerializerMethodField() # Лишняя строка.
    ingredients = RecipeIngredientSerializer(
        source='RecipeIngredient',
        many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    author = UsersSerializer()

    class Meta:
        """Мета класс отображение рецептов."""

        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        model = Recipe
        read_only_fields = fields

    def get_filter(self, obj):
        """Поиск наличия записи."""
        request = self.context.get('request', None)
        if request is not None and request.user.is_authenticated:
            return obj.filter(user=request.user).exists()
        return False

    def get_is_favorited(self, obj):
        """Проверка наличия в избранном."""
        return self.get_filter(obj.is_favorited)

    def get_is_in_shopping_cart(self, obj):
        """Проверка наличия в списке покупок."""
        return self.get_filter(obj.is_in_shopping_cart)

    # # Лишний метод.
    # def get_image(self, obj):
    #     """Получение картики рецепта."""
    #     if obj.image:
    #         return f'http://{settings.ALLOWED_HOSTS[0]}/
    # {obj.image.url.lstrip("/")}'
    #     return None


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Для сохранения ингредиентов рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(min_value=MIN_AMOUNT)

    class Meta:
        """Мета класс связной таблицы рецептов и ингредиентов."""

        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сохранение рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField(use_url=True, required=True)

    class Meta:
        """Мета класс для записи рецептов."""

        fields = '__all__'
        model = Recipe

    def validate_image(self, image):
        """Проверка что поле не пустое."""
        if image is None:
            raise serializers.ValidationError('Добавьте фотографию рецепта.')
        return image

    def get_double(self, data):
        """Проверка на дубли."""
        if len(data) > len(set(data)):
            raise serializers.ValidationError('Есть дублирующие элементы.')
        return data

    def validate_tags(self, tags):
        """Проверка на дубли тегов."""
        return self.get_double(tags)

    def validate_ingredients(self, ingredients_amounts):
        """Проверка на дубли ингредиентов."""
        ingredients = [
            ingredient_amont['id'] for ingredient_amont in ingredients_amounts
        ]
        self.get_double(ingredients)
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

    def get_ingredient(self, recipe, ingredients):
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
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.get_ingredient(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Изменение рецепта."""
        tags = validated_data.pop('tags')
        print(tags)
        ingredients = validated_data.pop('ingredients')
        print(ingredients)
        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags.clear()
            instance.tags.set(tags)
        if ingredients is not None:
            instance.ingredients.clear()
            self.get_ingredient(instance, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Отображение рецепта с полными данными."""
        return RecipeReadSerializer().to_representation(instance)


class MinRecipeSerializer(serializers.ModelSerializer):
    """Отображение рецепта с минимальными данными."""

    # image = serializers.SerializerMethodField(source='image.url')
# Лишняя строка.

    class Meta:
        """Мета класс рецепта с минимальными данными."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        # без него не выводится при добавлении в список покупок url
        """Получение картики рецепта."""
# # Лишний метод.
#         if obj.image:
#             return f'{settings.HOST}{obj.image.url}'
#         return None


class SubscriptionsSerializer(UsersSerializer):
    """Подписки."""

# Нельзя использовать обманывающие имена классов.
# Этот не выполяет сериализацию Подписки.
# См строку  model = DBUser.
# Поменяйте базовый класс и избавьтесь от строк is_subscribed,
# def get_is_subscribed. - Изменила
    # is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta(UsersSerializer.Meta):
        """Мета класс подписок."""

        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes(self, obj):
        """Выводим репецпы на кого подписались."""
        request = self.context.get('request')
        recipes_limit = int(request.GET.get('recipes_limit', 10**10))
        serializer = MinRecipeSerializer(
            obj.recipes.all()[:int(recipes_limit)],
            many=True,
            context={'request': request}
        )
        return serializer.data


class AvatarSerializer(serializers.ModelSerializer):
    """Аватар."""

    avatar = Base64ImageField(use_url=True, required=True)

    class Meta:
        """Мета данных аватара."""

        model = DBUser
        fields = ('avatar',)
