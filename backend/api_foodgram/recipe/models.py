from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser


def validate_hex(value):
    """Валидатор для цвета."""
    if value[0] != '#' or len(value) != 7:
        raise ValidationError(
            _('%(value)s не hex значение цвета!'),
            params={'value': value},
        )


class Ingredients(models.Model):
    """Модель Ингредиентов."""
    name = models.CharField(
        max_length=100,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        default='г.',
        verbose_name='Единица измерения',
        max_length=30,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredients'),
            models.CheckConstraint(
                check=~models.Q(name=models.F('measurement_unit')),
                name='author_not_measurement_unit_again',
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngredientsAmount(models.Model):
    """Промежуточная таблица."""
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ingredientsamount_set',
        verbose_name='Рецепт'
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredientsamount_set',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            RegexValidator(
                regex='^-',
                message='Минимальное количество не может быть < 0.'
            ),
            MinValueValidator(
                0,
                message='Минимальное количество не может быть < 0.'
            ),
            MaxValueValidator(
                100_000,
                message='Не ну 100-чка это перебор.'
            )
        ]
    )

    def __str__(self):
        return (
            f'{self.ingredients.name}: {self.amount}'
            f'{self.ingredients.measurement_unit}'
        )


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(max_length=30, verbose_name='Название')
    slug = models.SlugField(
        'slug',
        max_length=50,
        unique=True,
        db_index=True
    )
    hex_code = models.CharField(
        validators=[validate_hex],
        verbose_name='Цвет в 16 системе',
        max_length=7,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    """Модель Рецепта."""
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='recipe_tag',
        verbose_name='Теги'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipe',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through=IngredientsAmount,
        through_fields=('recipe', 'ingredients'),
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        max_length=30,
        verbose_name='Название блюда'
    )
    image = models.ImageField(
        verbose_name='Изображение блюда'
    )
    description = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин.',
        validators=[
            MinValueValidator(
                0,
                message='Время приготовления не может быть < 0.'
            ),
            MaxValueValidator(
                100_000,
                message='Длинные промежутки времени указывайте в описании.'
            )
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'name',),
                name='unique_recipe'),
        ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Модель Избранного."""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='in_favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ManyToManyField(
        Recipe,
        related_name='in_favorite',
        verbose_name='Рецепты',
    )

    def __str__(self) -> str:
        return f"{self.recipe.name} в избранном у {self.user.username}"


class ShoppingCart(models.Model):
    """Модель Список покупок."""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ManyToManyField(
        Recipe,
        related_name='in_shopping_cart',
        verbose_name='Рецепты',
    )

    def __str__(self) -> str:
        return f"{self.recipe.name} в списке покупок у {self.user.username}"
