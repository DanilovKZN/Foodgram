# Generated by Django 4.0.6 on 2022-07-09 09:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsamount',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.RegexValidator(message='Минимальное количество не может быть < 0.', regex='^-'), django.core.validators.MinValueValidator(0, message='Минимальное количество не может быть < 0.'), django.core.validators.MaxValueValidator(100000, message='Не ну 100-чка это перебор.')], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0, message='Время приготовления не может быть < 0.'), django.core.validators.MaxValueValidator(100000, message='Длинные промежутки времени указывайте в описании.')], verbose_name='Время приготовления, мин.'),
        ),
    ]
