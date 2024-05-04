from django.contrib import admin
from . import models


@admin.register(models.BotAccount)
class BotAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'handle', 'email', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('id', 'handle', 'email')
    list_per_page = 15


@admin.register(models.CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_account', 'status', 'creation_datetime')
    list_filter = ('user_account', 'status')
    date_hierarchy = 'creation_datetime'
    list_per_page = 15
    search_fields = ('id', 'user_account__email')


__all__ = ('BotAccountAdmin',)
