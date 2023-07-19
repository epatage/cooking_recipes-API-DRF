from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, SubscribeViewSet, TagViewSet,
                    UserViewSet)

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('recipes/favorites', RecipeViewSet, basename='favorites')
router.register(
    'recipes/shopping-cart',
    RecipeViewSet,
    basename='shopping_cart_recipes',
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite',
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart',
)
router.register('tags', TagViewSet)
router.register('tags/<int: tag_id>', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', UserViewSet)
router.register('users/me', UserViewSet)
router.register(
    'users/reset-password-confirm/<str:uid>/<str:token>/', UserViewSet
)
router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    SubscribeViewSet,
    basename='subscribe',
)
router.register('users/subscriptions', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
