"""
Модели.

DBUser - Пользователи.
SubscriptionsAdmin - Подписки.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import EMAIL_MAX_LENGTH, MAX_LENGTH_FOR_FIELDS
from users.validators import validate_username


class DBUser(AbstractUser):
    """Пользователи."""

    email = models.EmailField(
        'email',
        max_length=EMAIL_MAX_LENGTH,
        unique=True
    )
    username = models.CharField(
        'Никнейм',
        max_length=MAX_LENGTH_FOR_FIELDS,
        unique=True,
        validators=[validate_username]
    )
    first_name = models.CharField('Имя', max_length=MAX_LENGTH_FOR_FIELDS)
    last_name = models.CharField('Фамилия', max_length=MAX_LENGTH_FOR_FIELDS)
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


class Subscriptions(models.Model):
    """Подписки."""

    subscriber_user = models.ForeignKey(
        DBUser,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscriber_user'
    )
    author = models.ForeignKey(
        DBUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='author'
    )

    class Meta:
        """Мета данные подписок."""

        unique_together = ('subscriber_user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        """Отображение связи подписок."""
        return f'{self.subscriber_user} подписан на {self.author}'
