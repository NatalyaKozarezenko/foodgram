"""validate_username - Проверка имени пользователя."""

import re

from django.core.exceptions import ValidationError

from recipes.constants import OK_USERNAME


def validate_username(username):
    """Проверка имени пользователя."""
    invalid_chars = re.sub(OK_USERNAME, '', username)
    if invalid_chars:
        raise ValidationError(
            'Данные символы недопустимы: {}'.format(
                ''.join(set(invalid_chars))
            )
        )
    return username
