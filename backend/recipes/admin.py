from django.contrib import admin

from .models import (Ingredient, Recipe, Tag, IngredientRecipe,
                     Favorite, ShoppingCart)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 0
    min_num = 1


class TagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author')
    list_filter = ('author', 'name', 'tags')
    exclude = ('tags',)
    inlines = [IngredientRecipeInline, TagInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
