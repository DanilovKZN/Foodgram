from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipe.models import Recipe

from .models import CustomUser, Subscribe


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для модели CustomUser."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed',
        )

        validators = [
            UniqueTogetherValidator(
                queryset=CustomUser.objects.all(),
                fields=['username', 'email']
            )
        ]

    def get_is_subscribed(self, obj):
        request_user = self.context['request'].user
        if (
            request_user.is_authenticated
            and obj.following.filter(user=request_user).exists()
        ):
            return True
        return False

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Подписок."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )
        model = Subscribe

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user
        presence = Subscribe.objects.filter(
            author=obj.author,
            user=request_user).exists()
        return(
            request_user.is_authenticated
            and presence
        )

    def get_recipes_count(self, obj):
        return obj.author.recipe.count()

    def get_recipes(self, obj):
        recipes = RecipeFavoriteSerializer(
            obj.author.recipe.all(),
            many=True,
            read_only=True
        )
        return recipes.data


class UsersCreateSerializer(UserCreateSerializer):
    """
    Отдельный сериализатор для создания
    модели CustomUser.
    """
    class Meta(UserCreateSerializer.Meta):
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password'
        )

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        user.save()
        return user


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """
    Для вывода рецептов подписчика.
    Не работает, если находится в api.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
