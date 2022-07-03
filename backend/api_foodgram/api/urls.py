from django.urls import include, path
from rest_framework import routers

from users.views import SubscriptionsList, UserViewSet
from .utils import download_shopping_cart
from .views import IngredientsViewSet, RecipesViewSet, TagViewSet

app_name = 'api'

router_v1 = routers.DefaultRouter()


router_v1.register('recipes', RecipesViewSet, basename='recipes')
router_v1.register('ingredients', IngredientsViewSet, basename='ingredients')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('users', UserViewSet, basename='users')


urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionsList.as_view(),
        name='subsciptions'
    ),
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart'
    ),
    path('', include(router_v1.urls))
]
