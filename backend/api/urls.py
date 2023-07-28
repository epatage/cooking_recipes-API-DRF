from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from .views import (CustomUserViewSet, FavoriteViewSet, IngredientViewSet,
                    RecipeViewSet, ShoppingCartViewSet, SubscribeViewSet,
                    TagViewSet)

router = routers.DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register(
    r"recipes/(?P<recipe_id>\d+)/favorite",
    FavoriteViewSet,
    basename="favorite",
)
router.register(
    r"recipes/(?P<recipe_id>\d+)/shopping_cart",
    ShoppingCartViewSet,
    basename="shopping_cart",
)
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
router.register("users", CustomUserViewSet)
router.register(
    r"users/(?P<user_id>\d+)/subscribe",
    SubscribeViewSet,
    basename="subscribe",
)
router.register("users/subscriptions", CustomUserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
