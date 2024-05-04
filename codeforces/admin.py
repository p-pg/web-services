from django.contrib import admin
from . import models
from common import admin as common_admin


@admin.register(models.CFBotAccount)
class CFBotAccountAdmin(common_admin.BotAccountAdmin):
    pass


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


@admin.register(models.ProgrammingLanguage)
class ProgrammingLanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'website_id')
    search_fields = ('id', 'name', 'website_id')
    list_per_page = 20


@admin.register(models.CFCodeSubmission)
class CFCodeSubmissionAdmin(common_admin.CodeSubmissionAdmin):
    list_display = (*common_admin.CodeSubmissionAdmin.list_display, 'problem', 'programming_language', 'verdict')
    list_filter = (*common_admin.CodeSubmissionAdmin.list_filter, 'programming_language', 'verdict')
    search_fields = (*common_admin.CodeSubmissionAdmin.search_fields, 'problem__name')
    raw_id_fields = ('problem',)


__all__ = tuple()
