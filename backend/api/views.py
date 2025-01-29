"""??????."""

import django_filters
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.output import get_output
from api.paginations import Pagination
from api.permissions import IsAuthorOrRead
from api.serializers import (AvatarSerializer, IngredientSerializer,
                             MinRecipeSerializer, RecipeReadSerializer,
                             RecipeWriteSerializer, TagSerializer,
                             UsersSerializer, UsersSubscriptionsSerializer)
from recipes.models import (DBUser, Favorites, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Subscriptions, Tag)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Теги."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Продукты."""

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
    pagination_class = Pagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        """Сохранение автора."""
        serializer.save(author=self.request.user)

    def add_delete_data(self, request, models, **kwargs):
        """Добавление/удаление рецепта в Избранное или список покупок."""
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        user = request.user
        if request.method == 'POST':
            favorite, created = models.objects.get_or_create(
                recipe=recipe,
                user=user
            )
            if created:
                serializer = MinRecipeSerializer(
                    recipe, context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            raise serializers.ValidationError(
                {'errors': f'Рецепт {recipe.name} уже добавлен в'
                 f'{models._meta.verbose_name}.'}
            )
        elif request.method == 'DELETE':
            get_object_or_404(
                models.objects.filter(recipe=recipe, user=user)
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite',
            permission_classes=(permissions.IsAuthenticated,))
    def to_favorite(self, request, *args, **kwargs):
        """Добавление/удаление в (из) Избранного."""
        return self.add_delete_data(request, Favorites, **kwargs)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, *args, **kwargs):
        """Добавление/удаление в (из) списка покупок."""
        return self.add_delete_data(request, ShoppingCart, **kwargs)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
            permission_classes=(permissions.IsAuthenticated,))
    def generete_txt_file(self, request, *args, **kwargs):
        """Формирование файла txt из списка покупок."""
        user = DBUser.objects.get(username=request.user)
        recipes = Recipe.objects.filter(is_in_shopping_cart__user=user)
        ingredients_info = RecipeIngredient.objects.filter(
            recipe__in=recipes).select_related('ingredient').values(
                'amount',
                'ingredient__name',
                'ingredient__measurement_unit'
        )
        shopping_cart = {}
        for info in ingredients_info:
            key = (info['ingredient__name'] + ' ('
                   + info['ingredient__measurement_unit'] + ') — ')
            if key in shopping_cart:
                shopping_cart[key] = str(int(shopping_cart[key])
                                         + info['amount'])
            else:
                shopping_cart[key] = (str(info['amount']))
        return get_output(recipes, shopping_cart)

    @action(detail=True, methods=['get'], url_path='get-link',
            permission_classes=(permissions.AllowAny,))
    def get_link(self, request, pk):
        """Короткая ссылка на рецепт."""
        return Response(
            {'short-link': f'{settings.HOST}'
             + reverse_lazy('short_url_view', kwargs={'id': pk})},
            status=status.HTTP_200_OK
        )


class UsersViewSet(DjoserUserViewSet):
    """Пользователи."""

    queryset = DBUser.objects.all()
    serializer_class = UsersSerializer
    pagination_class = Pagination

    @action(detail=False, methods=['get'], url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        """Просмотр своих данных."""
        return super().me(request, *args, **kwargs)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request, *args, **kwargs):
        """Добавление/удаление аватора."""
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                request.user, data=request.data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            user = request.user
            if user.avatar:
                user.avatar.delete()
                user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request, *args, **kwargs):
        """Просмотр своих подписок."""
        subscriptions = Subscriptions.objects.filter(
            subscriber=request.user
        )
        authors = [subscription.author for subscription in subscriptions]
        paginator = Pagination()
        result_page = paginator.paginate_queryset(authors, request)
        serializer = UsersSubscriptionsSerializer(
            result_page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def add_subscribe(self, request, *args, **kwargs):
        """Редактирование подписок."""
        subscriber = request.user
        author = self.get_object()
        if request.method == 'POST':
            if subscriber == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription, created = Subscriptions.objects.get_or_create(
                subscriber=subscriber,
                author=author
            )
            if not created:
                return Response(
                    {'errors': f'Вы уже подписаны на пользователя {author}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = UsersSubscriptionsSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(Subscriptions.objects.filter(
                subscriber=subscriber,
                author=author)
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
