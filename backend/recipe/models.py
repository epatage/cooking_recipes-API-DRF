from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

User = get_user_model()

CHOICES = (
    ('Gray', 'Серый'),
    ('Black', 'Чёрный'),
    ('White', 'Белый'),
    ('Ginger', 'Рыжий'),
    ('Mixed', 'Смешанный'),
)


class Tag(models.Model):
    """Теги рецептов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        null=False,
        blank=False,
    )
    color = models.CharField(
        max_length=7,
        choices=CHOICES,
        null=True,
        blank=True,
        unique=True,
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Слаг содержит недопустимый символ',
        )]
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингридиенты рецептов."""
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
    )
    measurement_unit = models.CharField(
        max_length=200,
        null=False,
        blank=False,
    )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Рецепт."""
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=False,
        blank=False,
    )
    text = models.TextField(
        'Описание',
        null=True,
        blank=False,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    cooking_time = models.IntegerField(
        blank=False,
        null=False,
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Связь M2M рецептов и Тэгов."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(models.Model):
    """Связь M2M рецептов и ингредиентов."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Favorite(models.Model):
    """Избранные рецепты."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_user_recipe_favorite'
            )
        ]


class ShoppingCart(models.Model):
    """Список покупок."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_user_recipe_shopping_card'
            )
        ]
