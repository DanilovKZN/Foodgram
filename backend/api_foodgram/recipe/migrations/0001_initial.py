# Generated by Django 2.2.16 on 2022-07-03 08:46

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions
import recipe.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название ингредиента')),
                ('measurement_unit', models.CharField(default='г.', max_length=30, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='IngredientsAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0, message='Минимальное количество не может быть <= 0.'), django.core.validators.MaxValueValidator(100000, message='Не ну 100-чка это перебор.')], verbose_name='Количество')),
                ('ingredients', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredientsamount_set', to='recipe.Ingredients', verbose_name='Ингредиент')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Название блюда')),
                ('image', models.ImageField(upload_to='', verbose_name='Изображение блюда')),
                ('description', models.TextField(verbose_name='Описание')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0, message='Время приготовления не может быть <= 0.'), django.core.validators.MaxValueValidator(100000, message='Длинные промежутки времени указывайте в описании.')], verbose_name='Время приготовления, мин.')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipe', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('ingredients', models.ManyToManyField(related_name='recipes', through='recipe.IngredientsAmount', to='recipe.Ingredients', verbose_name='Ингредиенты')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Название')),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('hex_code', models.CharField(max_length=7, validators=[recipe.models.validate_hex], verbose_name='Цвет в 16 системе')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ManyToManyField(related_name='in_shopping_cart', to='recipe.Recipe', verbose_name='Рецепты')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='in_shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='recipe_tag', to='recipe.Tag', verbose_name='Теги'),
        ),
        migrations.AddField(
            model_name='ingredientsamount',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredientsamount_set', to='recipe.Recipe', verbose_name='Рецепт'),
        ),
        migrations.AddConstraint(
            model_name='ingredients',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_ingredients'),
        ),
        migrations.AddConstraint(
            model_name='ingredients',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, name=django.db.models.expressions.F('measurement_unit')), name='author_not_measurement_unit_again'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='recipe',
            field=models.ManyToManyField(related_name='in_favorite', to='recipe.Recipe', verbose_name='Рецепты'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='in_favorite', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(fields=('author', 'name'), name='unique_recipe'),
        ),
    ]
