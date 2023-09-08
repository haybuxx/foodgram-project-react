from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscribtionsListAPIView,
                    TagViewSet, UserViewSet)

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('users/subscriptions/', SubscribtionsListAPIView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
]
