from django_filters import rest_framework as filters

from recipe.models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(
        field_name="tags", lookup_expr="slug", method="filter_tags"
    )
    is_favorited = filters.CharFilter(
        field_name="is_favorited", method="filter_favorited"
    )
    is_in_shopping_cart = filters.CharFilter(
        field_name="is_in_shopping_cart", method="filter_shopping_cart"
    )
    author = filters.CharFilter(field_name="author", method="filter_author")

    class Meta:
        model = Recipe
        fields = ("tags", "is_favorited", "is_in_shopping_cart", "author")

    def filter_tags(self, queryset, tags, slug):
        return queryset.filter(tags__slug=slug)

    def filter_favorited(self, queryset, is_favorited, enum):
        if enum:
            return queryset.filter(recipes__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, is_in_shopping_cart, enum):
        if enum:
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset

    def filter_author(self, queryset, author, author_id):
        if author_id:
            return queryset.filter(author_id=author_id)
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )

    class Meta:
        model = Ingredient
        fields = ("name",)

    def filter_ingredients(self, queryset, ingredients, name):
        return queryset.filter(name=name)
