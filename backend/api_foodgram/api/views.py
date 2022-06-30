from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from recipe.models import Ingredients, Recipe, Tag
from users.models import Favorites, ShoppingCart

from .filters import RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOnly, IsAuthorOrAdminReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeFavoriteSerializer, RecipesListSerializer,
                          TagSerializer)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all().order_by('-pk')
    permission_classes = (IsAuthorOrAdminReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipesListSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipesListSerializer(
            instance=serializer.instance,
            context={'request': self.request},
        )
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

    @action(
        methods=(['post', 'delete']),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Обработка избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        flag = 'Favorite'
        data = [recipe]
        return favorite_shop_card(flag, data, request)

    @action(
        methods=(['post', 'delete']),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Обработка списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        users_shopping_cart = ShoppingCart.objects.get_or_create(
            user=request.user
        )
        flag = 'Shop'
        data = [recipe, users_shopping_cart]
        return favorite_shop_card(flag, data, request)


def favorite_shop_card(flag, data, request):
    """
    Устранение дублирования кода для
    Favorite и ShopCard
    """
    if request.method == 'POST':
        if flag == 'Favorite':
            try:
                Favorites.objects.create(user=request.user, recipe=data[0])
            except Exception:
                return Response(
                    {"Ошибка": "Рецепт уже есть в избранном!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            print(data[1])
            if data[1][0].recipe.filter(pk__in=(data[0].pk,)).exists():
                return Response(
                    {"Ошибка": "Рецепт уже есть в списке покупок!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data[1][0].recipe.add(data[0])
        serializer = RecipeFavoriteSerializer(data[0])
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    else:
        if flag == 'Favorite':
            recipe = Favorites.objects.filter(user=request.user, recipe=data[0])
            if recipe:
                recipe.delete()
                return Response(
                    {"Оповещение": "Рецепт удален из избранного!"},
                    status=status.HTTP_204_NO_CONTENT
                )
        else:
            if data[1][0].recipe.filter(pk__in=(data[0].pk,)).exists():
                data[1][0].recipe.remove(data[0])
                return Response(
                    {"Оповещение": "Рецепт удален из списка покупок!"},
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {"Ошибка": "Рецепта нет!"},
                status=status.HTTP_400_BAD_REQUEST
            )


class IngredientsViewSet(viewsets.ModelViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_field = ('name',)
    permission_classes = (IsAdminOnly,)
    pagination_class = LimitPageNumberPagination


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_field = ('slug',)
