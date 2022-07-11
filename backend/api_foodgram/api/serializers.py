from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipe.models import (Favorite, Ingredients, IngredientsAmount, Recipe,
                           ShoppingCart, Tag)
from users.serializers import UserSerializer


COOKING_TIME_VALIDATION = 'Время не может быть меньше 0'
VAL_NOT_ZERO = 'Убедитесь, что значение количества ингредиента больше 0'
VAL_NOT_INT = 'Убедитесь, что значение ингредиента число.'
HEX_LEN_NUMBERS = 7


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    color = serializers.CharField(source='hex_code')

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag

    def validate_color(self, value):
        if len(value) != HEX_LEN_NUMBERS:
            raise serializers.ValidationError('Неверная длина поля!')
        if value[0] != '#':
            raise serializers.ValidationError('Цвет должен начинаться с "#"')
        return value


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredients


class IngredientsAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для модели IngredientsAmount."""
    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source='ingredients'
    )
    name = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
        source='ingredients'
    )
    measurement_unit = serializers.SlugRelatedField(
        read_only=True,
        slug_field='measurement_unit',
        source='ingredients'
    )

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиента, входящего в рецепт."""
    amount = serializers.SerializerMethodField(error_messages={'Ошибка': VAL_NOT_ZERO})

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'amount',)

    def get_amount(self, obj):
        amount_inngr = get_object_or_404(
            obj.ingredientsamount_set,
            ingredients_id=obj.id, recipe_id=self.context.get('id')
        ).amount
        if int(amount_inngr) <= 0:
            raise serializers.ValidationError(VAL_NOT_ZERO)
        return amount_inngr


class RecipesListSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра модели Recipe."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsAmountSerializer(
        many=True,
        read_only=True,
        source='ingredientsamount_set'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    text = serializers.CharField(source='description', read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['name', 'author']
            ),
        ]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления модели Recipe."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = serializers.SerializerMethodField(error_messages={'Ошибка': VAL_NOT_ZERO})
    image = Base64ImageField()
    text = serializers.CharField(source='description')

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'name',
            'text',
            'cooking_time',
            'image',
            'tags',
            'author'
        )
        read_only_field = ('id', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['name', 'author']
            ),
        ]

    def get_ingredients(self, value):
        """Получение ключа ingredients."""
        ingredient_list = IngredientAmountCreateSerializer(
            value.ingredients.all(),
            many=True,
            read_only=True,
            context={'id': value.id}
        ).data
        return ingredient_list

    def teg_ing_for_create_and_update(self, recipe, data):
        tags_list = []
        tags = data.pop('tags')
        ingredients = data.pop('ingredients')
        for tag in tags:
            current_tag = get_object_or_404(Tag, pk=tag.pk)
            tags_list.append(current_tag)
        recipe.tags.set(tags_list)
        objects = (
            IngredientsAmount(
                recipe=recipe,
                ingredients=get_object_or_404(
                    Ingredients,
                    pk=recipe_ingredient['id']),
                amount=recipe_ingredient['amount']
            ) for recipe_ingredient in ingredients
        )
        IngredientsAmount.objects.bulk_create(objects)
        return recipe

    def create(self, validated_data):
        data = {}
        data['tags'] = validated_data.pop('tags')
        data['ingredients'] = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        return self.teg_ing_for_create_and_update(recipe, data)

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        instance.name = validated_data.get(
            'name',
            instance.name
        )
        instance.image = validated_data.get(
            'image',
            instance.image
        )
        instance.description = validated_data.get(
            'description',
            instance.description
        )
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.save()
        instance = self.teg_ing_for_create_and_update(instance, validated_data)
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {
                    'ingredients': 'Нужен хотя бы один ингредиент для рецепта'
                }
            )
        ingr_set = set()
        for ingredient_item in ingredients:
            ingr_set.add(ingredient_item['id'])
            if int(ingredient_item['amount']) < 0:
                raise serializers.ValidationError(VAL_NOT_ZERO)
        if len(ingr_set) < len(ingredients):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными'
            )
        data['ingredients'] = ingredients
        return data


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого вывода Recipe в Избранных и Списке покупок."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
