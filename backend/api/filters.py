from django_filters import rest_framework as filters

from recipe.models import Recipe


class TagFilter(filters.FilterSet):
    tags = filters.CharFilter(
        field_name="tags", lookup_expr='slug', method='filter_tags'
    )

    class Meta:
        model = Recipe
        fields = ['tags']

    def filter_tags(self, queryset, tags, slug):
        print((queryset))
        return queryset.filter(tags__slug=slug)


class TagFavoriteFilter(filters.FilterSet):
    tags = filters.CharFilter(
        field_name="tags", lookup_expr='slug', method='filter_tags'
    )

    class Meta:
        model = Recipe
        fields = ['tags']

    def filter_tags(self, queryset, tags, slug):
        return queryset.filter(tags__slug=slug)
