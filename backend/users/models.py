from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""
    email = models.EmailField(
        'Email адрес',
        max_length=254,
        unique=True,
        null=True,
        blank=False,
    )
    username = models.CharField(
        'Username',
        max_length=150,
        unique=True,
        null=True,
        blank=False,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )
    first_name = models.CharField(
        max_length=150,
        null=True,
        blank=False,
    )
    last_name = models.CharField(
        max_length=150,
        null=True,
        blank=False,
    )
    password = models.CharField(
        max_length=150,
        null=True,
        blank=False,
    )

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Подписки на авторов рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
        null=False,
        blank=False,
    )
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор рецепта',
        null=False,
        blank=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribing'],
                name='unique_follow',
            )
        ]
