import base64

from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipes.constants import HTTP_DOMEN, MESSAGE, MIN_VALUE
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import DBUser, Subscriptions
from users.validators import validate_username


def get_http_image(image):
    return f'{HTTP_DOMEN}/{image.url.lstrip("/")}'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = DBUser
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def validate_username(self, username):
        validate_username(username)
        return username

    def get_is_subscribed(self, obj):
        return Subscriptions.objects.filter(author=obj.id).exists()

    def get_avatar(self, obj):
        if obj.avatar:
            return get_http_image(obj.avatar)
        return None


class UserRegSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = DBUser
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        )

    def validate_username(self, username):
        validate_username(username)
        return username


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    image = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(
        source='recipe', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    author = UserSerializer()

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        model = Recipe
        read_only_fields = fields

    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        if request is not None:
            if request.user.is_authenticated:
                return obj.is_favorited.filter(username=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request', None)
        if request is not None:
            if request.user.is_authenticated:
                return obj.is_in_shopping_cart.filter(
                    username=request.user
                ).exists()
        return False

    def get_image(self, obj):
        if obj.image:
            return get_http_image(obj.image)
        return None


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    amount = serializers.IntegerField(
        validators=(MinValueValidator(MIN_VALUE, message=MESSAGE),)
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        fields = '__all__'
        model = Recipe

    def validate_tags(self, values):
        double_values = values
        for value in double_values[:-1]:
            double_values = double_values[1:]
            if value in double_values:
                raise serializers.ValidationError(
                    'Есть дублирующие элементы.'
                )
        return values

    def validate_ingredients(self, values):
        double_values = values
        for value in double_values[:-1]:
            double_values = double_values[1:]
            for double_value in double_values:
                if value['ingredient'] == double_value['ingredient']:
                    raise serializers.ValidationError(
                        'Есть дублирующие элементы.'
                    )
        return values

    def validate(self, value):
        if not value.get('ingredients'):
            raise serializers.ValidationError(
                'Добавьте хотя бы 1 ингредиент.'
            )
        if not value.get('tags'):
            raise serializers.ValidationError(
                'Добавьте хотя бы 1 тег.'
            )
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(name=ing['ingredient']),
                amount=ing['amount']
            ) for ing in ingredients
        )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            RecipeIngredient.objects.bulk_create(
                RecipeIngredient(
                    recipe=instance,
                    ingredient=Ingredient.objects.get(name=ing['ingredient']),
                    amount=ing['amount']
                ) for ing in ingredients
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer().to_representation(instance)


class MinRecipeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        if obj.image:
            return get_http_image(obj.image)
        return None


class SubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta:
        model = DBUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = MinRecipeSerializer(
            recipes, many=True, context={'request': request}
        )
        return serializer.data


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(use_url=True, required=False)

    class Meta:
        model = DBUser
        fields = ('avatar',)

    def to_representation(self, instance):
        return AvatarHttpSerializer().to_representation(instance)


class AvatarHttpSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = DBUser
        fields = ('avatar',)

    def get_avatar(self, obj):
        if obj.avatar:
            return get_http_image(obj.avatar)
        return None


class ShorturlSerializer(serializers.Serializer):
    short_link = serializers.CharField(source='short-link')

    class Meta:
        fields = ('short_link',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'short_link' in representation:
            representation['short-link'] = representation.pop('short_link')
        return representation
