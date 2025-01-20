"""
Настройка админки.

UserAdmin - Пользователи.
SubscriptionsAdmin - Подписки.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import DBUser, Subscriptions


@admin.register(DBUser)
class UserAdmin(BaseUserAdmin):
    """Пользователи."""

    list_display = ('email', 'username', 'first_name', 'last_name')
    list_display_links = ('email', 'username')
    search_fields = ('email', 'username')


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    """Подписки."""

    list_display = ('subscriber_user', 'author')
    search_fields = ('subscriber_user', 'author')
