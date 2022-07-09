from django.contrib import admin

from .models import Ingredients, IngredientsAmount, Recipe, Tag


class RecipeIngredientsInline(admin.TabularInline):
    model = IngredientsAmount
    min_num = 1
    extra = 0


class RecipeTagsInline(admin.TabularInline):
    model = Tag
    min_num = 1
    extra = 0


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'recipes_in_favorites')
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'
    list_per_page = 10
    inlines = [RecipeIngredientsInline]

    def recipes_in_favorites(self, obj):
        return obj.in_favorite.count()


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    search_fields = ('name__startswith',)
    empty_value_display = '-пусто-'
    list_per_page = 10
    ordering = ('pk',)


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'hex_code')
    prepopulated_fields = {'slug': ('name', )}
    list_filter = ('name',)
    search_fields = ('name', 'slug',)
    empty_value_display = '-пусто-'
    list_per_page = 10
    inlines = [RecipeTagsInline]


@admin.register(IngredientsAmount)
class IngredientsAmountAdmin(admin.ModelAdmin):
    list_display = (
        'ingredients', 'amount',
    )
    empty_value_display = '-пусто-'
    list_per_page = 10
