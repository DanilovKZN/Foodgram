from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from recipe.models import Favorite, Ingredients, Recipe, ShoppingCart, Tag
from .filters import RecipeFilter, IngredientsFilter
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
        model = Favorite.objects.get_or_create(
            user=request.user
        )
        return favorite_shop_card(recipe, request, model)

    @action(
        methods=(['post', 'delete']),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Обработка списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        model = ShoppingCart.objects.get_or_create(
            user=request.user
        )
        return favorite_shop_card(recipe, request, model)


def favorite_shop_card(data, request, model):
    """
    Устранение дублирования кода для
    Favorite и ShoppingCard
    """
    if request.method == 'POST':
        if data.author == request.user:
            return Response(
                {"Ошибка": "Нельзя добавить свой рецепт!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if (model[0].recipe.filter(pk__in=(data.pk,)).exists()):
            return Response(
                {"Ошибка": "Рецепт уже есть присутствует!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        model[0].recipe.add(data)
        serializer = RecipeFavoriteSerializer(data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    if model[0].recipe.filter(pk__in=(data.pk,)).exists():
        model[0].recipe.remove(data)
        return Response(
            {"Оповещение": "Рецепт удален!"},
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
    permission_classes = (IsAdminOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_field = ('slug',)
