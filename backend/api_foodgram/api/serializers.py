import json
from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator


from recipe.models import (
    Tag,
    Ingredients,
    IngredientsAmount,
    Recipe
)

from users.serializers import  UserSerializer

from django.shortcuts import get_object_or_404


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    color = serializers.CharField(source='hex_code')
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag
        
    def validate_color(self, value):
        if len(value) != 7 :
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
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
    )
    
    class Meta:
        model = IngredientsAmount
        fields = ('id', 'amount',)


class RecipesListSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра модели Recipe."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsAmountSerializer(many=True, read_only=True, source='ingredientsamount')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
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
            'created',  
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
        # user = self.context['request'].user
        # if user.is_authenticated:
        #     return user.shopping_cart.recipes.filter(pk__in=(obj.pk,)).exists()
        return False

class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания модели Recipe.""" 
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = IngredientAmountCreateSerializer(
        many=True,
    )
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
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['name', 'author']
            ),
        ]

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
                ingredients = get_object_or_404(Ingredients, pk=recipe_ingredient['id']),
                amount = recipe_ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.ingredients.clear()
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get('description', instance.description)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.save()
        for tag in tags:
            current_tag = get_object_or_404(Tag, pk=tag.pk)
            instance.tags.add(current_tag)
        for recipe_ingredient in ingredients:
            IngredientsAmount.objects.create(
                recipe=Recipe.objects.get(pk=instance.pk),
                ingredients = get_object_or_404(Ingredients, pk=recipe_ingredient['id']),
                amount = recipe_ingredient['amount']
            )
        return instance

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хотя бы один ингридиент для рецепта'})
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredients, id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError('Ингридиенты должны быть уникальными')
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) < 0:
                raise serializers.ValidationError({
                    'ingredients': ('Убедитесь, что значение количества ингредиента больше 0')})
        data['ingredients'] = ingredients
        return data     


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)