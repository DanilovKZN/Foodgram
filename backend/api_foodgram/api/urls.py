from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
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
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
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
