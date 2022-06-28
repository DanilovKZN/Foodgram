from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
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

FILE_NAME = 'shopping_cart.txt'
KRISHA = """
Для ваших кулинарных подвигов необходимо преобрести:\r\n
"""
POGREB = """
\nУдачных покупок и вкусных блюд!
"""


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all().order_by('-created')
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
        if request.method == 'POST':
            try:
                Favorites.objects.create(user=request.user, recipe=recipe)
            except Exception:
                return Response(
                    {"Ошибка": "Рецепт уже есть в избранном!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeFavoriteSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        recipe = Favorites.objects.filter(user=request.user, recipe=recipe)
        if recipe:
            recipe.delete()
            return Response(
                {"Оповещение": "Рецепт удален из избранного!"},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {"Ошибка": "Рецепта нет в избранном!"},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        if request.method == 'POST':
            if users_shopping_cart[0].recipe.filter(
                pk__in=(recipe.pk,)
            ).exists():
                return Response(
                    {"Ошибка": "Рецепт уже есть в списке покупок!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            users_shopping_cart[0].recipe.add(recipe)
            serializer = RecipeFavoriteSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if users_shopping_cart[0].recipe.filter(pk__in=(recipe.pk,)).exists():
            users_shopping_cart[0].recipe.remove(recipe)
            return Response(
                {"Оповещение": "Рецепт удален из списка покупок!"},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"Ошибка": "Рецепта нет в списке покупок!"},
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


@api_view(['GET'])
def download_shopping_cart(request):
    """Функция печати списка покупок."""
    if not request.user.is_authenticated:
        return Response(
            {"Оповещение": "Авторизируйтесь, пожалуйста!"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    recipes = request.user.shopping_cart.recipe.prefetch_related('ingredients')
    if not recipes:
        return Response(
            {"Оповещение": "Список покупок пуст!"},
            status=status.HTTP_400_BAD_REQUEST
        )
    name_ingredients = []
    wight_ingredients = []
    ingredients_to_write = {}
    ingredients_for_download = ''
    for recipe in recipes:
        for i in recipe.ingredients.values():
            name_ingredients.append([i['name'], i['measurement_unit']])
        for i in recipe.ingredientsamount_set.values():
            wight_ingredients.append(i['amount'])
    for i in range(len(name_ingredients)):
        name_ingredients[i].append(wight_ingredients[i])
    for ingredient in name_ingredients:
        if not ingredient[0] in ingredients_to_write:
            ingredients_to_write[ingredient[0]] = [ingredient[1], ingredient[2]]
        else:
            ingredients_to_write[ingredient[0]][1] += ingredient[2]
    for ingr_for_down in ingredients_to_write:
        ingredients_for_download += (
            f'{ingr_for_down}'
            f' - {ingredients_to_write[ingr_for_down][1]}'
            f'{ingredients_to_write[ingr_for_down][0]}.\r\n'
        )
    response = HttpResponse(
        KRISHA + ingredients_for_download + POGREB,
        content_type='text/plain,charset=utf8'
    )
    response['Content-Disposition'] = f'attachment; filename={FILE_NAME}'
    return response
