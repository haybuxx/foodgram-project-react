from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.filters import RecipeFilter
from api.permissions import IsOwnerOrReadOnly
from api.utils import create_object, delete_object
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User

from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          SubscriptionReadSerializer, SubscriptonSerializer,
                          TagSerializer, UserSerializer)


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
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return super().get_serializer_class()

    def add_to_base(self, request, model, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        _, created = model.objects.get_or_create(
            recipe=recipe, user=request.user
        )
        if created:
            serializer = FavoriteRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(status=HTTP_400_BAD_REQUEST)

    def delete_from_base(self, user, model, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        databse_obj = model.objects.filter(
            user=user, recipe=recipe
        )
        if not databse_obj.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        databse_obj.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete'),
        url_path='favorite',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_to_base(request, Favorite, pk)
        return self.delete_from_base(request.user, Favorite, pk)

    @action(
        methods=('post', 'delete'),
        url_path='shopping_cart',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_to_base(request, ShoppingCart, pk)
        return self.delete_from_base(request.user, ShoppingCart, pk)

    @action(
        methods=('get',),
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shop_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_sum=Sum('amount'))
        wishlist = ''
        for ingredient in ingredients:
            wishlist += (f'{ingredient["ingredient__name"]}: '
                         f'{ingredient["total_sum"]}')
            wishlist += f'{ingredient["ingredient__measurement_unit"]}.\n'
        response = HttpResponse(wishlist, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=wishlist.txt'
        return response


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id):
        if request.method == 'POST':
            serializer = create_object(
                request,
                id,
                SubscriptonSerializer,
                SubscriptionReadSerializer,
                User
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        delete_object(request, id, User, Subscription)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user = request.user
        authors = User.objects.filter(subscribing__user=user)

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
