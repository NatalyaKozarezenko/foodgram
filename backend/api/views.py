"""Представления приложения api."""

import locale
from datetime import date

import django_filters
from django.db.models import Sum
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
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
            _, created = models.objects.get_or_create(
                recipe=recipe,
                user=user
            )
            if created:
                return Response(
                    MinRecipeSerializer(
                        recipe,
                        context={'request': request}
                    ).data,
                    status=status.HTTP_201_CREATED
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
        recipes = Recipe.objects.filter(
            is_in_shopping_cart__user=user).select_related('author').values(
                'id',
                'name',
                'author__username'
        )
        ingredients_info = RecipeIngredient.objects.filter(
            recipe__in=[recipe['id'] for recipe in recipes]).select_related(
                'ingredient').values(
                    'ingredient__name',
                    'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')
        # locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
        # не установлен на сервере ru_RU.UTF-8
        # locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        current_date = date.today().strftime("%d %b %Y")
        template = {
            'ingredients':
                '{number}) {total_amount} ({measurement_unit}) - {name}',
            'recipe': '{number}) {name} ({author})'
        }
        return FileResponse(
            get_output(recipes, ingredients_info, current_date, template),
            filename='ListShopWithProducts_{}.txt'.format(current_date),
            as_attachment=True,
            content_type='text/plain'
        )

    @action(detail=True, methods=['get'], url_path='get-link',
            permission_classes=(permissions.AllowAny,))
    def get_link(self, request, pk):
        """Короткая ссылка на рецепт."""
        if not Recipe.objects.filter(id=pk).exists():
            raise Http404('Рецепта с id={pk} не существует.')
        return Response(
            {'short-link': request.build_absolute_uri(
                reverse('short_url_view', args=[pk])
            )},
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
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request, *args, **kwargs):
        """Просмотр своих подписок."""
        subscriptions = request.user.subscribers.all()
        paginator = Pagination()
        return paginator.get_paginated_response(
            UsersSubscriptionsSerializer(
                paginator.paginate_queryset(
                    [subscription.author for subscription in subscriptions],
                    request
                ),
                many=True,
                context={'request': request}
            ).data
        )

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def add_subscribe(self, request, *args, **kwargs):
        """Редактирование подписок."""
        subscriber = request.user
        author = self.get_object()
        if request.method == 'POST':
            if subscriber == author:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя.'
                )
            _, created = Subscriptions.objects.get_or_create(
                subscriber=subscriber,
                author=author
            )
            if not created:
                raise serializers.ValidationError(
                    f'Вы уже подписаны на пользователя {author}.'
                )
            serializer = UsersSubscriptionsSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Subscriptions.objects.filter(
            subscriber=subscriber,
            author=author)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
