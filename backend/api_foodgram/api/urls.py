from django.urls import include, path, re_path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework import routers

from users.views import SubscriptionsList, UserViewSet

from .views import (
    IngredientsViewSet,
    RecipesViewSet,
    TagViewSet,
    download_shopping_cart
)

app_name = 'api'

router_v1 = routers.DefaultRouter()


router_v1.register(r'recipes', RecipesViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    re_path(r'^v1/auth/', include('djoser.urls')),
    path('v1/auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('v1/auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
    path(
        'v1/users/subscriptions/',
        SubscriptionsList.as_view(),
        name='subsciptions'
    ),
    path(
        'v1/recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart'
    ),
    path('v1/', include(router_v1.urls))
]
