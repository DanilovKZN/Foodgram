from rest_framework import filters, mixins, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, renderer_classes

from django_filters.rest_framework.backends import DjangoFilterBackend

from recipe.models import Recipe, Ingredients, Tag
from users.models import CustomUser, Subscribe, Favorites
from users.serializers import SubscribeSerializer, UserSerializer

from .serializers import (
    RecipesListSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeCreateSerializer,
    RecipeFavoriteSerializer
)

from .permissions import IsAuthorOrAdminReadOnly, IsUserOrAdminReadOnly, IsAdminOnly

from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet as DjoserUserViewSet



class ListCreateViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('created')
    permission_classes = (IsAuthorOrAdminReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=(['post', 'delete']),
        detail=True,
        permission_classes=(IsAuthenticated,)
    ) 
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            try:
                Favorites.objects.create(user=request.user, recipe=recipe)
            except:
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


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    # нужен кастомный фильтр
    permission_classes = (IsAdminOnly,)
    pagination_class = PageNumberPagination


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOnly,)
    pagination_class = PageNumberPagination


class UserPageViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsUserOrAdminReadOnly,)

    def get_queryset(self):
        recipe = get_object_or_404(
            CustomUser,
            id=self.kwargs.get('user_id')
        )
        return recipe


class SubscribeViewSet(ListCreateViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author__username',)

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )



