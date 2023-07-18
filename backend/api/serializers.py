import base64
import re

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipe.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                           RecipeTag, ShoppingCart, Tag)
from users.models import Subscription, User


class Base64ImageField(serializers.ImageField):
    """Сериалайзер изображений."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей"""
    is_subscribed = serializers.SerializerMethodField(
        source='subscription_set'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        if not self.context:
            return False
        return Subscription.objects.filter(
            user=self.context['request'].user, subscribing=obj
        ).exists()


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = 'email', 'username', 'first_name', 'last_name', 'password'

    def create(self, validated_data):
        """Хеширует пароль при создании пользователя."""
        user = super(SignUpSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate(self, data):
        """Запрещает пользователям присваивать себе имя me
        и использовать повторные username и email и запрещает
        использовать недопустимые символы."""
        regex = re.sub(r'^[\w.@+-]+\Z', '', data.get('username'))
        if data.get('username') in regex:
            raise serializers.ValidationError(
                f'Имя пользователя не должно содержать {regex}'
            )
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" запрещено'
            )
        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError(
                'Данное имя пользователя уже занято!'
            )
        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError(
                'Данный Email уже занят!'
            )
        return data


class PasswordSerializer(serializers.ModelSerializer):
    """Изменение пароля."""
    new_password = serializers.StringRelatedField()
    current_password = serializers.StringRelatedField(source='user')

    class Meta:
        model = User
        fields = 'new_password', 'current_password'


class TagSerializer(serializers.ModelSerializer):
    """Тэги."""
    class Meta:
        fields = '__all__'
        model = Tag

    def to_internal_value(self, data):
        """Для создания/редактирования рецептов с использованием id тегов."""
        return data


class RecipeTagSerializer(serializers.ModelSerializer):
    """Создание связей рецептов и тэгов."""
    id = serializers.SerializerMethodField(source='tag')
    name = serializers.SerializerMethodField(source='tag')
    color = serializers.SerializerMethodField(source='tag')
    slug = serializers.SerializerMethodField(source='tag')

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = RecipeTag

    def get_id(self, obj):
        return obj.tag.id

    def get_name(self, obj):
        return obj.tag.name

    def get_color(self, obj):
        return obj.tag.color

    def get_slug(self, obj):
        return obj.tag.slug


class IngredientSerializer(serializers.ModelSerializer):
    """Ингридиенты."""
    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Связи Рецептов и ингредиентов (с количеством)."""
    id = serializers.SerializerMethodField(source='ingredient')
    name = serializers.SerializerMethodField(source='ingredient')
    measurement_unit = serializers.SerializerMethodField(source='ingredient')
    amount = serializers.SerializerMethodField(source='amount')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    def get_amount(self, obj):
        return obj.amount


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    """Создание связей рецептов и ингредиентов."""
    id = serializers.IntegerField()

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient

    def validate_amount(self, value):
        if not (value >= 1):
            raise serializers.ValidationError(
                'Убедитесь, что это значение больше либо равно 1.'
            )
        return value


class RecipeGetSerializer(serializers.ModelSerializer):
    """Для GET запросов рецептов."""
    author = UserSerializer()
    image = Base64ImageField(required=False, allow_null=True)
    tags = RecipeTagSerializer(source='recipetag_set', many=True)
    ingredient = RecipeIngredientsSerializer(
        source='recipeingredient_set', many=True
    )
    is_favorited = serializers.SerializerMethodField(source='favorite_set')
    is_in_shopping_cart = serializers.SerializerMethodField(
        source='shoppingcart_set'
    )

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredient',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            user=self.context['request'].user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(
            user=self.context['request'].user, recipe=obj
        ).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    """Для POST запросов создания/редактирования рецепта."""
    ingredients = RecipeIngredientPostSerializer(many=True)
    tags = TagSerializer()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )
        model = Recipe

    def to_representation(self, instance):
        """Для корректного контекста возврата при создании рецепта."""
        request = self.context.get('request')
        context = {'request': request}
        return RecipeGetSerializer(instance, context=context).data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag = Tag.objects.get(id=tag)
            RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        for ingredient in ingredients:
            amount = ingredient.pop('amount')
            current_ingredient = Ingredient.objects.get(**ingredient)
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=current_ingredient, amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        old_ingredients = RecipeIngredient.objects.filter(recipe=instance)
        old_ingredients.delete()
        old_tags = RecipeTag.objects.filter(recipe=instance)
        old_tags.delete()

        for tag in tags:
            current_tag = Tag.objects.get(id=tag)
            RecipeTag.objects.create(recipe=instance, tag=current_tag)
        for ingredient in ingredients:
            amount = ingredient.pop('amount')
            current_ingredient = Ingredient.objects.get(**ingredient)
            RecipeIngredient.objects.create(
                recipe=instance, ingredient=current_ingredient, amount=amount
            )

        instance.text = validated_data.get('text', instance.text)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        instance.save()
        return instance


class RecipeGetListSerializer(serializers.ModelSerializer):
    """Для GET запросов сериалайзеров Избранного и Списка покупок."""
    author = UserSerializer()
    image = Base64ImageField(required=False, allow_null=True)
    tags = RecipeTagSerializer(source='recipetag_set', many=True)
    ingredient = RecipeIngredientsSerializer(
        source='recipeingredient_set', many=True
    )

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredient',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    """Для поля рецепты в сериалайзере подписок."""
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class RecipeShoppingCartSerializer(serializers.ModelSerializer):
    """Для сериалайзера Списка покупок."""
    ingredient = RecipeIngredientsSerializer(
        source='recipeingredient_set', many=True
    )

    class Meta:
        fields = ('id', 'ingredient')
        model = Recipe


class SubscriptionSerializer(serializers.ModelSerializer):
    """Список подписок на авторов."""
    email = serializers.SerializerMethodField(source='subscribing')
    id = serializers.SerializerMethodField(source='subscribing')
    username = serializers.SerializerMethodField(source='subscribing')
    first_name = serializers.SerializerMethodField(source='subscribing')
    last_name = serializers.SerializerMethodField(source='subscribing')
    is_subscribed = serializers.BooleanField(read_only=True, default=True)
    recipes = RecipeSubscribeSerializer(
        source='subscribing.recipes', many=True
    )
    recipes_count = serializers.SerializerMethodField(source='subscribing')

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        model = Subscription

    def get_email(self, obj):
        return obj.subscribing.email

    def get_id(self, obj):
        return obj.subscribing.id

    def get_username(self, obj):
        return obj.subscribing.username

    def get_first_name(self, obj):
        return obj.subscribing.first_name

    def get_last_name(self, obj):
        return obj.subscribing.last_name

    def get_recipes_count(self, obj):
        return obj.subscribing.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Подписаться/отписаться на авторов."""
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )
    subscribing = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault(),

    )

    class Meta:
        fields = '__all__'
        model = Subscription


class FavoritesSerializer(serializers.ModelSerializer):
    """Список избранных рецептов."""
    recipe = RecipeGetListSerializer()

    class Meta:
        fields = '__all__'
        model = Favorite


class FavoriteAddSerializer(serializers.ModelSerializer):
    """Добавление рецепта в избранное."""
    name = serializers.SerializerMethodField(source='recipe')
    image = Base64ImageField(required=False, source='recipe.image')
    cooking_time = serializers.SerializerMethodField(source='recipe')

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Favorite

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time

    def get_name(self, obj):
        return obj.recipe.name

    def get_image(self, obj):
        return obj.recipe.image


class FavoriteDeleteSerializer(serializers.ModelSerializer):
    """Удаление рецепта из Избранное."""
    class Meta:
        fields = '__all__'
        model = Favorite


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Просмотр Списка покупок."""
    recipe = RecipeGetListSerializer()

    class Meta:
        fields = '__all__'
        model = ShoppingCart


class ShoppingCartAddSerializer(serializers.ModelSerializer):
    """Добавление рецепта в список покупок."""
    name = serializers.SerializerMethodField(source='recipe')
    image = Base64ImageField(
        required=False, allow_null=True, source='recipe.image'
    )
    cooking_time = serializers.SerializerMethodField(source='recipe')

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = ShoppingCart

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time

    def get_name(self, obj):
        return obj.recipe.name

    def get_image(self, obj):
        return obj.recipe.image


class ShoppingCartDeleteSerializer(serializers.ModelSerializer):
    """Удаление рецепта из списка покупок."""
    name = serializers.SerializerMethodField(source='recipe')
    image = serializers.SerializerMethodField(source='recipe')
    cooking_time = serializers.SerializerMethodField(source='recipe')

    class Meta:
        fields = '__all__'
        model = ShoppingCart
