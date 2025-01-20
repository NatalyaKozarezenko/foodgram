"""
Перечень функций и классов.

redirect_view - Получение рецепта по короткой ссылке.
RecipeFilter - Фильтр по данным рецепта.
TagViewSet - Теги
IngredientFilter - Фильтр по начальным значением ингредиента.
IngredientViewSet - Ингредиенты.
RecipeViewSet - Рецепты.
CostomsViewSet - Пользователи.
AvatarViewSet - Аватор пользователя.
"""

import short_url

from api.permissions import IsAuthorOrRead
from api.serializers import (AvatarSerializer, IngredientSerializer,
                             MinRecipeSerializer, RecipeReadSerializer,
                             RecipeWriteSerializer, ShorturlSerializer,
                             SubscriptionsSerializer, TagSerializer,
                             UserRegSerializer, UserSerializer)
from django.apps import apps
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
import django_filters
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.constants import HTTP_DOMEN, NAME_FILE
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import filters, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import DBUser, Subscriptions


def redirect_view(request, tiny):
    """Получение рецепта по короткой ссылке."""
    model = apps.get_model('recipes', 'Recipe')
    try:
        id = short_url.decode_url(tiny)
    except ValueError:
        raise Http404('Не правильно закодированный индентификатор.')
    obj = get_object_or_404(model, pk=id)
    return redirect(obj)


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
            return Recipe.objects.filter(is_favorited=user)
        elif int(value) == 0:
            return Recipe.objects.exclude(is_favorited=user)
        else:
            return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        """Проверка рецепта в списке покупок."""
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if value else queryset
        if int(value) == 1:
            return Recipe.objects.filter(is_in_shopping_cart=user)
        elif int(value) == 0:
            return Recipe.objects.exclude(is_in_shopping_cart=user)
        else:
            return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Теги."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientFilter(django_filters.FilterSet):
    """Фильтр по начальным значением ингредиента."""

    name = django_filters.CharFilter(
        field_name='name', lookup_expr='istartswith'
    )

    class Meta:
        """Мета класс фильтра ингредиентов."""

        model = Ingredient
        fields = ['name']


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter
    )
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrRead,
    )
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.action == 'list':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        """Сохранение автора."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite',
            permission_classes=(permissions.IsAuthenticated,))
    def to_favorite(self, request, *args, **kwargs):
        """Добавление/удаление в (из) Избранного."""
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        user = request.user
        exist = recipe.is_favorited.filter(username=user).exists()
        if request.method == 'POST':
            if not exist:
                recipe.is_favorited.add(user)
                serializer = MinRecipeSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Рецепт уже есть в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            if exist:
                recipe.is_favorited.remove(user)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепта не было в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, *args, **kwargs):
        """Добавление/удаление в (из) списка покупок."""
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        user = request.user
        exist = recipe.is_in_shopping_cart.filter(username=user).exists()
        if request.method == 'POST':
            if not exist:
                recipe.is_in_shopping_cart.add(user)
                serializer = MinRecipeSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Рецепт уже есть в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            if exist:
                recipe.is_in_shopping_cart.remove(user)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепта не было в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
            permission_classes=(permissions.IsAuthenticated,))
    def generete_txt_file(self, request, *args, **kwargs):
        """Формирование файла txt из списка покупок."""
        text = 'Список покупок:\n'
        user = DBUser.objects.get(username=request.user)
        shopping_cart = {}
        recipes = user.shopping_carts.all()
        for recipe in recipes:
            for ingredient in recipe.ingredients.all():
                amount = RecipeIngredient.objects.get(
                    recipe=recipe, ingredient=ingredient).amount
                key = (ingredient.name + ' ('
                       + ingredient.measurement_unit + ') — ')
                if key in shopping_cart:
                    shopping_cart[key] = str(int(shopping_cart[key]) + amount)
                else:
                    shopping_cart[key] = (str(amount))
        number_purchase = 1
        for key, value in shopping_cart.items():
            text += str(number_purchase) + '. ' + key + value + '\n'
            number_purchase += 1
        with open(NAME_FILE, 'w') as file:
            file.write(text)
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={NAME_FILE}'
        return response

    @action(detail=True, methods=['get'], url_path='get-link',
            permission_classes=(permissions.AllowAny,))
    def get_link(self, request, *args, **kwargs):
        """Короткая ссылка на рецепт."""
        tinyid = short_url.encode_url(int(kwargs.get('pk')))
        test = reverse_lazy('short_url_view', kwargs={'tiny': tinyid})
        data = {'short-link': f'{HTTP_DOMEN}' + test}
        serializer = ShorturlSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CostomsViewSet(DjoserUserViewSet):
    """Пользователи."""

    queryset = DBUser.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.action == 'create':
            return UserRegSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return UserSerializer

    @action(detail=False, methods=['get'], url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        """Просмотр своих данных."""
        author = get_object_or_404(DBUser, username=request.user)
        serializer = UserSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request, *args, **kwargs):
        """Просмотр своих подписок."""
        subscriptions = Subscriptions.objects.filter(
            subscriber_user=request.user
        )
        authors = [subscription.author for subscription in subscriptions]
        paginator = PageNumberPagination()
        paginator.page_size_query_param = 'limit'
        paginator.page_size = request.query_params.get('limit', 6)
        result_page = paginator.paginate_queryset(authors, request)
        serializer = SubscriptionsSerializer(
            result_page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe',
            permission_classes=(permissions.IsAuthenticated,))
    def add_subscribe(self, request, *args, **kwargs):
        """Редактирование подписок."""
        subscriber_user = request.user
        author = self.get_object()
        subscription = Subscriptions.objects.filter(
            subscriber_user=subscriber_user,
            author=author
        )
        if request.method == 'POST':
            if subscriber_user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if subscription.exists():
                return Response(
                    {'errors': f'Вы уже подписаны на пользователя {author}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscriptions.objects.create(
                subscriber_user=subscriber_user,
                author=author
            )
            serializer = SubscriptionsSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'Вы не были подписаны на пользователя {author}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class AvatarViewSet(APIView):
    """Аватор пользователя."""

    queryset = DBUser.objects.all()
    serializer_class = AvatarSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request):
        """Добавление аватора пользователя."""
        serializer = AvatarSerializer(request.user, data=request.data)
        if request.data.get('avatar') is None:
            raise serializers.ValidationError(
                '"avatar": ["Обязательное поле."]'
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request):
        """Удаление аватора пользователя."""
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
