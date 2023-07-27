from django.contrib import admin
from django.db.models import Count

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "favorite_added",
    )
    search_fields = ("author", "name", "tags")
    list_filter = ("author", "name", "tags")
    empty_value_display = "-пусто-"

    def favorite_added(self, obj):
        return obj.favorite_added

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(favorite_added=Count("recipes"))
        return queryset


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)
    empty_value_display = "-пусто-"


admin.site.register(Tag)

admin.site.register(RecipeIngredient)

admin.site.register(RecipeTag)

admin.site.register(Favorite)

admin.site.register(ShoppingCart)
