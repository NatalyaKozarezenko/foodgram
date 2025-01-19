import random
import string

from django.db import models


def generate_short_id():
    length = 6
    while True:
        short_id = ''.join(
            random.choices(string.ascii_letters + string.digits, k=length)
        )
        if not ShortenedUrl.objects.filter(short_id=short_id).exists():
            break
    return short_id


class ShortenedUrl(models.Model):
    original_url = models.URLField(max_length=1024)
    short_id = models.CharField(
        max_length=6,
        unique=True,
        default=generate_short_id
    )

    def __str__(self):
        return self.original_url
