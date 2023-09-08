from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)

from api.filters import RecipeFilter
from api.permissions import IsOwnerOrReadOnly
from api.utils import delete_object
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User

from .serializers import (FavoriteOrCartSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeFavoriteSerializer,
                          RecipeSerializer, SubscriptionReadSerializer,
                          SubscriptonSerializer, TagSerializer, UserSerializer)


class TagViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return super().get_serializer_class()

    def add_to_base(self, request, model, pk, serializer_class):
        recipe = get_object_or_404(Recipe, pk=pk)
        _, created = model.objects.get_or_create(
            recipe=recipe, user=request.user
        )
        if created:
            serializer = serializer_class(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response({"errors": "Обект уже существует!"},
                        status=HTTP_400_BAD_REQUEST)

    def delete_from_base(self, user, model, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        databse_obj = model.objects.filter(
            user=user, recipe=recipe
        )
        if not databse_obj.exists():
            return Response({"errors": "Обекта не существует!"},
                            status=HTTP_400_BAD_REQUEST)
        databse_obj.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete'),
        url_path='favorite',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=RecipeFavoriteSerializer
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_to_base(request, Favorite, pk,
                                    self.get_serializer_class())
        return self.delete_from_base(request.user, Favorite, pk)

    @action(
        methods=('POST', 'DELETE'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = FavoriteOrCartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            recipe = ShoppingCart.objects.filter(user=request.user,
                                                 recipe__id=pk)
            if recipe.exists():
                recipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        cart_items = ShoppingCart.objects.filter(user=request.user)
        cart = {}
        for item in cart_items:
            recipe = item.recipe
            for ingredient in recipe.ingredients.all():
                if ingredient.id in cart.keys():
                    cart[
                        ingredient.id
                    ]['amount'] += IngredientRecipe.objects.get(
                        recipe=recipe, ingredient=ingredient).amount
                else:
                    cart[ingredient.id] = {
                        "name": ingredient.name,
                        "amount": IngredientRecipe.objects.get(
                            recipe=recipe,
                            ingredient=ingredient
                        ).amount,
                        "measurement_unit": ingredient.measurement_unit
                    }

        result = []
        for id, data in cart.items():
            result.append(
                f"{data['name']}: {data['amount']} {data['measurement_unit']}"
            )
        response = HttpResponse('\n'.join(result).encode(
            'utf-8'), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="list.txt"'
        return response


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk):
        if request.method == 'POST':
            author = get_object_or_404(User, id=pk)
            subscription, created = Subscription.objects.get_or_create(
                user=request.user, author=author)
            if created:
                serializer = self.get_serializer(author)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response({
                "errors": "Exists"}, status=status.HTTP_400_BAD_REQUEST)
        delete_object(request, pk, User, Subscription)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user = request.user
        subscriptions = Subscription.objects.filter(user=user)
        authors = User.objects.filter(
            id__in=[s.author_id for s in subscriptions])

        paged_queryset = self.paginate_queryset(authors)
        serializer = SubscriptionReadSerializer(
            paged_queryset,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class SubscribtionsListAPIView(generics.ListAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptonSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
