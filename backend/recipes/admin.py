from django.contrib import admin

from .models import Ingredient, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class Recipe(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class Ingredient(admin.ModelAdmin):
    pass
