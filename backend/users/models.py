from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Подписчик', related_name='subscriptions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор', related_name='subscribers')

    class Meta:
        verbose_name='Подписка'
        verbose_name_plural='Подписки'
        constraints=[
            models.UniqueConstraint(fields=['user', 'author'], name='uniq_user_author'),
        ]
