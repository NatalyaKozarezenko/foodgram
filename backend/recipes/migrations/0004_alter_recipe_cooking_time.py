# Generated by Django 4.2.17 on 2025-01-15 21:16

from django.db import migrations, models
import recipes.models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_recipeingredient_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[recipes.models.min_value], verbose_name='Время приготовления (в минутах)'),
        ),
    ]
