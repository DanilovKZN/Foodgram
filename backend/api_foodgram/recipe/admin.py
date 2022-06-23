from django.contrib import admin

from .models import Recipe, Ingredients, Tag, IngredientsAmount


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author',)
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'

@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'

@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'hex_code')
    prepopulated_fields = {'slug': ('name', )}
    list_filter = ('name',)
    search_fields = ('name', 'slug',)
    empty_value_display = '-пусто-'

@admin.register(IngredientsAmount)
class IngredientsAmountAdmin(admin.ModelAdmin):
    list_display = (
        'ingredients', 'amount',
    )
    list_filter = ('ingredients',)
    empty_value_display = '-пусто-'
