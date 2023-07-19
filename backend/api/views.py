from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipe.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscription, User

from .filters import TagFilter
from .permissions import AuthorOrReadOnly, OwnerOrAdmin, ReadOnly
from .renderers import TextDataRenderer
from .serializers import (FavoriteAddSerializer, FavoriteDeleteSerializer,
                          IngredientSerializer, RecipeGetSerializer, RecipeGetAuthorizedSerializer,
                          RecipePostSerializer, ShoppingCartAddSerializer,
                          ShoppingCartDeleteSerializer, ShoppingCartSerializer,
                          SignUpSerializer, SubscribeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserBasicSerializer, UserAuthorizedSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты и всё, что с ними связано."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ('name',)
    filterset_class = TagFilter
    ordering = ('-pub_date',)

    def get_serializer(self, *args, **kwargs):
        """Для передачи пользователя в контекст запроса."""
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipePostSerializer
        if self.request.user == AnonymousUser():
            return RecipeGetSerializer
        return RecipeGetAuthorizedSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        """Редактирует рецепт."""
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        serializer = self.get_serializer(recipe, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(
        methods=['delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def delete(self, request, *args, **kwargs):
        """Удаляет рецепт."""
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        url_path='shopping-cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, *args, **kwargs):
        """Отдает список покупок с добавленными рецептами."""
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        serializer = ShoppingCartSerializer(shopping_cart, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        url_path='favorites',
        permission_classes=[IsAuthenticated],
        ordering=('-pub_date',),
    )
    def favorites(self, request, *args, **kwargs):
        """Отдает список избранных рецептов."""
        recipes = Recipe.objects.prefetch_related(
            "recipes"
        ).filter(recipes__user=request.user)
        recipes = self.filter_queryset(recipes)
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated],
        renderer_classes=[TextDataRenderer]
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        """Функция формирования и отдачи файла с продуктами для покупок."""
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        print('SHHH', shopping_cart)
        shopping_list = dict()
        recipes = shopping_cart.values()
        for recipe in recipes:
            recipe_cart = get_object_or_404(Recipe, id=recipe['recipe_id'])
            ingredients = recipe_cart.recipeingredient_set.all()
            for ingr in ingredients:
                if ingr.ingredient.name not in shopping_list:
                    shopping_list[ingr.ingredient.name] = ingr.amount
                else:
                    shopping_list[ingr.ingredient.name] += ingr.amount

        return Response(shopping_list, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Тэги рецептов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингридиенты."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class SubscribeViewSet(viewsets.ModelViewSet):
    """Подписаться на автора."""
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        return user

    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        if self.request.user == user:
            raise ValidationError('Нельзя подписываться на себя !')
        subscribe = Subscription.objects.filter(
            user=self.request.user, subscribing=user
        )
        if subscribe.exists():
            raise ValidationError('Подписка уже существует !')

        serializer.save(user=self.request.user, subscribing=user)

    @action(
        methods=['delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def delete(self, request, *args, **kwargs):
        """Удаляет подписку на автора."""
        subscribing = get_object_or_404(User, id=self.kwargs.get('user_id'))
        subscribe = Subscription.objects.filter(
            user=request.user, subscribing=subscribing
        )
        if not subscribe.exists():
            raise ValidationError('Подписка уже удалена !')
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Добавить/удалить рецепт в избранное."""
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == 'create':
            return FavoriteAddSerializer
        return FavoriteDeleteSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        queryset = Favorite.objects.filter(
            user=self.request.user, recipe=recipe
        )
        if queryset.exists():
            raise ValidationError('Рецепт уже добавлен в избранное!')

        serializer.save(user=self.request.user, recipe=recipe)

    @action(
        methods=['delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def delete(self, request, *args, **kwargs):
        """Удаляет рецепт из избранного."""
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        if not favorite.exists():
            raise ValidationError('Рецепт уже удален !')
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Добавить/удалить рецепт в Список покупок."""
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == 'create':
            return ShoppingCartAddSerializer
        return ShoppingCartDeleteSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        queryset = ShoppingCart.objects.filter(
            user=self.request.user, recipe=recipe
        )
        if queryset.exists():
            raise ValidationError('Рецепт уже добавлен в список покупок!')

        serializer.save(user=self.request.user, recipe=recipe)

    @action(methods=['delete'], detail=True)
    def delete(self, request, *args, **kwargs):
        """Удаляет рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        shopping_cart_recipe = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        )
        if not shopping_cart_recipe.exists():
            raise ValidationError('Рецепта нет в списке покупок !')
        shopping_cart_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет пользователей."""
    queryset = User.objects.all()
    serializer_class = UserBasicSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        """Меняет сериалайзер при POST для создания пользователя."""
        if self.action == 'create':
            return SignUpSerializer
        print('self', self)
        return UserBasicSerializer

    @action(
        methods=['get'],
        detail=False,
        url_path='subscriptions',
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request, *args, **kwargs):
        """Подписки пользователя на авторов рецептов."""
        subscribtions = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(subscribtions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def me(self, request, *args, **kwargs):
        """Запрос к своей странице пользователя."""
        serializer = UserAuthorizedSerializer(request.user)
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

    @action(
        methods=['post'],
        detail=False,
        permission_classes=[OwnerOrAdmin],
        url_path='set_password')
    def set_password(self, request, *args, **kwargs):
        """Смена пароля."""
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        if not user.check_password(current_password):
            return Response(
                {"current_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.password = make_password(new_password)
        user.save()
        return Response(
            {"message": "Password updated successfully."},
            status=status.HTTP_200_OK
        )
