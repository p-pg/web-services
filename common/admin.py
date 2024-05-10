from django.contrib import admin
from . import models


@admin.register(models.BotAccount)
class BotAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'handle', 'email', 'is_verified', 'status')
    list_filter = ('is_verified',)
    search_fields = ('id', 'handle', 'email')
    date_hierarchy = 'last_assignment'
    list_per_page = 15


@admin.register(models.CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'bot_account', 'status', 'creation_datetime')
    list_filter = ('bot_account', 'status')
    date_hierarchy = 'creation_datetime'
    list_per_page = 15
    search_fields = ('id', 'bot_account__email')


__all__ = ('BotAccountAdmin',)
