from django.contrib import admin
from . import models


@admin.register(models.UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'handle', 'email', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('id', 'handle', 'email')
    list_per_page = 15


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    list_per_page = 20


@admin.register(models.ProblemSet)
class ProblemSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_name')
    search_fields = ('id', 'name', 'short_name')
    list_per_page = 20


@admin.register(models.Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'phase', 'is_frozen', 'difficulty')
    list_filter = ('type', 'phase', 'is_frozen')
    search_fields = ('id', 'name', 'kind')
    list_per_page = 15


@admin.register(models.Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'contest', 'problem_set', 'index', 'name', 'type')
    raw_id_fields = ('contest', 'problem_set', 'tags')
    search_fields = ('id', 'name', 'contest__name', 'problem_set__name', 'tags__name')
    list_per_page = 15


@admin.register(models.Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'user_account', 'programming_language', 'verdict', 'creation_datetime')
    list_filter = ('user_account', 'programming_language', 'verdict')
    date_hierarchy = 'creation_datetime'
    list_per_page = 15
    search_fields = ('id', 'problem__name', 'user_account__email')
    raw_id_fields = ('problem',)


__all__ = tuple()
