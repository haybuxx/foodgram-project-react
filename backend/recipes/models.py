from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import CASCADE, ForeignKey, Model, UniqueConstraint

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        default='#00ff7f',
        null=True,
        blank=True,
        unique=True,
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=200,
        unique=True,
        validators=[RegexValidator(r'^[-a-zA-Z0-9_]+$')],
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=200
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement')]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количесвто'
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.measurement_unit})'
            f' - {self.amount} '
        )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    image = models.ImageField(verbose_name='Картинка')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления в минутах'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient,
        through=IngredientRecipe,
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class FavoritesShopCart(Model):
    user = ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=CASCADE
    )
    recipe = ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=CASCADE
    )

    class Meta:
        abstract = True


class FavoriteRecipe(FavoritesShopCart):

    class Meta:
        default_related_name = 'favorites'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('recipe_id',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe}'


class ShoppingCart(FavoritesShopCart):

    class Meta:
        default_related_name = 'shop_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('recipe_id',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe}'
