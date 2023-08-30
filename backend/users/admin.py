from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email')
    search_fields = ('first_name',)
    list_filter = ('email', 'first_name')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']
    search_fields = ['user', 'author']
    list_filter = ['user', 'author']
    empty_value_display = '-пусто-'


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
