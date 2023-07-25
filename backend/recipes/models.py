from django.db import models


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=7,
        default='#00ff7f',
        null=True,
        blank=True,
        unique=True,
    )
    slug = models.SlugField(
        'Slug тега',
        max_length=200,
        unique=True,
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