from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from users.models import Subscription


def create_object(request, pk, serializer_in, serializer_out, model):
    user = request.user.id
    obj = get_object_or_404(model, id=pk)

    data_recipe = {'user': user, 'recipe': obj.id}
    data_subscribe = {'user': user, 'author': obj.id}

    if model is Recipe:
        serializer = serializer_in(data=data_recipe)
    else:
        serializer = serializer_in(data=data_subscribe)

    serializer.is_valid(raise_exception=True)
    serializer.save()
    serializer_to_response = serializer_out(obj, context={'request': request})
    return serializer_to_response


def delete_object(request, pk, model_object, model_for_delete_object):
    user = request.user

    if model_for_delete_object is Subscription:
        obj_for_delete = get_object_or_404(
            model_for_delete_object, user=user, author=pk
        )
    else:
        obj_for_delete = get_object_or_404(
            model_for_delete_object, user=user, recipe=pk
        )

    obj_for_delete.delete()
