from django_filters.rest_framework import CharFilter, FilterSet, NumberFilter

from recipe.models import Recipe


class RecipeFilter(FilterSet):
    """Фильтр для рецептов по тегам, избранному и списку покупок."""
    is_favorited = NumberFilter(method='filter_is_favorited', )
    tags = CharFilter(field_name='tags__slug', method='filter_tags')
    is_in_shopping_cart = NumberFilter(method='filter_is_in_shopping_cart', )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', )

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(in_favorite__user=self.request.user)
        return queryset

    def filter_tags(self, queryset, name, tags):
        return queryset.filter(tags__slug=tags)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(in_shopping_cart__user=self.request.user.id)
        return queryset
