import re

from django.core.exceptions import ValidationError

from users.constants import EXAMPLE


def validate_username(username):
    invalid_chars = re.sub(EXAMPLE, '', username)
    if invalid_chars:
        raise ValidationError(
            'Данные символы недопустимы: {}'.format(
                ''.join(set(invalid_chars))
            )
        )
    return username
