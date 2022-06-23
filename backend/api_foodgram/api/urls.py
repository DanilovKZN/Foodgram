from django.urls import path, include, re_path
from rest_framework import routers
from djoser.views import TokenDestroyView, TokenCreateView


from .views import (
    IngredientsViewSet,
    TagViewSet,
    RecipesViewSet,
)

from users.views import UserViewSet

app_name = 'api'

router_v1 = routers.DefaultRouter()


router_v1.register(r'recipes', RecipesViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    re_path(r'^v1/auth/', include('djoser.urls')),
    path('v1/auth/token/login/', TokenCreateView.as_view(), name='login' ),
    path('v1/auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
    path('v1/', include(router_v1.urls)),
]
