from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class CustomUserAdmin(UserAdmin):
    pass


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']
    search_fields = ['user', 'author']
    list_filter = ['user', 'author']
    empty_value_display = '-пусто-'


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
