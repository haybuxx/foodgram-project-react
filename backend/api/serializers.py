from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import User, Subscription


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

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
        user = self.context.get('request').user
        if not user.is_anonymous:
            return user.subscriptions.filter(user=obj).exists()
        return False


class IngredientRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    
    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(source='recipe_ingredients', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        return False

    def get_is_in_shopping_cart(self, obj):
        return False


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'amount',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'name',
            'text',
            'cooking_time',
            'ingredients',
            'image',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags', None)
        if not tags:
            raise ValidationError('Выберите хотя бы один тег')
        ingredients = validated_data.pop('ingredients', None)
        if not ingredients:
            raise ValidationError('Укажите зотя бы один ингредиент')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(ingredient=i.get(
                'id'), recipe=recipe, amount=i.get('amount'))
            for i in ingredients
        ])
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags:
            instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients', None)
        if ingredients:
            instance.ingredients.clear()
            IngredientRecipe.objects.bulk_create([
                IngredientRecipe(ingredient=i.get(
                    'id'), recipe=instance, amount=i.get('amount'))
                for i in ingredients
            ])
        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data


class SubscriptonSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True, source='author.recipe_set')
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
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

    def get_is_subscribed(self, obj):
        return obj.author.subscriptions.filter(author=obj.user).exists()

    def get_recipes_count(self, obj):
        return obj.author.recipe_set.count()

class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
