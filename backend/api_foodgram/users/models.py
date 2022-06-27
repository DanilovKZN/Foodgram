from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import BooleanField, CharField, EmailField


class CustomUser(AbstractUser):
    email = EmailField(max_length=254, unique=True)
    username = CharField(
        max_length=150,
        unique=True,
    )
    first_name = CharField(max_length=150, blank=True)
    last_name = CharField(max_length=150, blank=True)
    password = CharField(
        max_length=254,
        default='',
        validators=[MinLengthValidator(8, message='Минимум 8 символов')]
    )
    is_blocked = BooleanField('Заблочен', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_email_for_username')
        ]    


class Subscribe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='uning_fields'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_follows'
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.username} подписан на {self.author.username}"


class Favorites(models.Model):
    """Модель Избранного."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='in_favorite',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'recipe.Recipe',
        on_delete=models.CASCADE,
        related_name='in_favorite',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='uning_fields'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('recipe')),
                name='prevent_follows'
            )
        ]

    def __str__(self) -> str:
        return f"{self.following.username} в избранном у {self.user.username}"


class ShoppingCart(models.Model):
    """Модель Список покупок."""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ManyToManyField(
        'recipe.Recipe',
        related_name='in_shopping_cart',
        verbose_name='Рецепты',
    )

    def __str__(self) -> str:
        return f"{self.recipe.name} в избранном у {self.user.username}"
