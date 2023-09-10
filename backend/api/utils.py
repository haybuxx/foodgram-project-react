from django.shortcuts import get_object_or_404

from users.models import Subscription

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
