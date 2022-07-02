from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

FILE_NAME = 'shopping_cart.txt'
KRISHA = """
Для ваших кулинарных подвигов необходимо преобрести:\r\n
"""
POGREB = """
\nУдачных покупок и вкусных блюд!
"""


@api_view(['GET'])
def download_shopping_cart(request):
    """Функция печати списка покупок."""
    if not request.user.is_authenticated:
        return Response(
            {"Оповещение": "Авторизируйтесь, пожалуйста!"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    recipes = request.user.in_shopping_cart.recipe.prefetch_related('ingredients')
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
