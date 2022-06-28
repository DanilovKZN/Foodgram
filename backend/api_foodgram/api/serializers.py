from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipe.models import Ingredients, IngredientsAmount, Recipe, Tag
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import ShoppingCart
from users.serializers import UserSerializer

VAL_NOT_ZERO = 'Убедитесь, что значение количества ингредиента больше 0'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    color = serializers.CharField(source='hex_code')

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag

    def validate_color(self, value):
        if len(value) != 7:
            raise serializers.ValidationError('Неверная длина поля!')
        elif value[0] != '#':
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
    amount = serializers.SerializerMethodField()

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'amount',)

    def get_amount(self, obj):
        return get_object_or_404(
            obj.ingredientsamount_set,
            ingredients_id=obj.id, recipe_id=self.context.get('id')
        ).amount


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
        if user.is_authenticated:
            return user.in_favorite.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


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
    ingredients = serializers.SerializerMethodField()
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

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag = get_object_or_404(Tag, pk=tag.pk)
            recipe.tags.add(current_tag)
        for recipe_ingredient in ingredients:
            IngredientsAmount.objects.create(
                recipe=recipe,
                ingredients=get_object_or_404(
                    Ingredients,
                    pk=recipe_ingredient['id']
                ),
                amount=recipe_ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
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
        for tag in tags:
            current_tag = get_object_or_404(Tag, pk=tag.pk)
            instance.tags.add(current_tag)
        for recipe_ingredient in ingredients:
            IngredientsAmount.objects.create(
                recipe=Recipe.objects.get(pk=instance.pk),
                ingredients=get_object_or_404(
                    Ingredients,
                    pk=recipe_ingredient['id']
                ),
                amount=recipe_ingredient['amount']
            )
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {
                    'ingredients': 'Нужен хотя бы один ингридиент для рецепта'
                }
            )
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredients,
                id=ingredient_item['id']
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными'
                )
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) < 0:
                raise serializers.ValidationError(
                    {
                        'ingredients': (VAL_NOT_ZERO)
                    }
                )
        data['ingredients'] = ingredients
        return data


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого вывода Recipe в Избранных и Списке покупок."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
