# Generated by Django 2.2.16 on 2022-06-25 14:08

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import recipe.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Название ингредиента')),
                ('measurement_unit', models.CharField(default='г.', max_length=30, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'unique_together': {('name', 'measurement_unit')},
            },
        ),
        migrations.CreateModel(
            name='IngredientsAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(validators=[django.core.validators.MinValueValidator(0, message='Минимальное количество не может быть <= 0.'), django.core.validators.MaxValueValidator(100000, message='Не ну 100-чка это перебор.')], verbose_name='Количество')),
                ('ingredients', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredientsamount', to='recipe.Ingredients', verbose_name='Ингредиент')),
            ],
            options={
                'verbose_name': 'Количество ингредиента',
                'verbose_name_plural': 'Количество ингредиентов',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Название')),
                ('slug', models.CharField(max_length=30)),
                ('hex_code', models.CharField(max_length=7, validators=[recipe.models.validate_hex], verbose_name='Цвет в 16 системе')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Название блюда')),
                ('image', models.ImageField(upload_to='', verbose_name='Изображение блюда')),
                ('description', models.TextField(verbose_name='Описание')),
                ('cooking_time', models.IntegerField(validators=[django.core.validators.MinValueValidator(0, message='Время приготовления не может быть <= 0.'), django.core.validators.MaxValueValidator(1440, message='Время приготовления не может быть больше суток.')], verbose_name='Время приготовления, мин.')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('ingredients', models.ManyToManyField(related_name='recipes', through='recipe.IngredientsAmount', to='recipe.Ingredients', verbose_name='Ингредиенты')),
                ('tags', models.ManyToManyField(blank=True, related_name='recipe_tag', to='recipe.Tag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
            },
        ),
        migrations.AddField(
            model_name='ingredientsamount',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredientsamount', to='recipe.Recipe', verbose_name='Рецепт'),
        ),
    ]
