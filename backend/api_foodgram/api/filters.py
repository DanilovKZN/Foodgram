from django_filters.rest_framework import CharFilter, FilterSet, NumberFilter

from recipe.models import Recipe


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""
    is_favorited = NumberFilter(method='filter_is_favorited', )
    tags = CharFilter(field_name='tags__slug', method='filter_tags')

    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited', ) #'author', 

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(in_favorite__user=self.request.user)
        return queryset

    def filter_tags(self, queryset, name, tags):
        return queryset.filter(tags__slug=tags)
