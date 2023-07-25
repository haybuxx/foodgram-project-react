from django.contrib import admin
from .models import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']
    search_fields = ['user', 'author']
    list_filter = ['user', 'author']
    empty_value_display = '-пусто-'


admin.site.register(Subscription, SubscriptionAdmin)
