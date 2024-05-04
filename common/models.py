from django.db import models
from . import fields, functions
from django.core.validators import MinLengthValidator


class BotAccount(models.Model):
    class Status(models.IntegerChoices):
        READY = 1, 'Ready'
        IN_USE = 2, 'In Use'
        AUTHENTICATION_FAILED = 3, 'Authentication Failed'

    handle = fields.ICharField(max_length=64, unique=True)
    clear_password = models.CharField(validators=(MinLengthValidator(5),), max_length=32)
    email = fields.IEmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.READY)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f'{self.email} : {self.handle}'


class CodeSubmission(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 1, 'Pending'
        IN_PROGRESS = 2, 'In Progress'
        UPLOAD_FAILED = 3, 'Upload Failed'
        SUBMITTED = 4, 'Submitted'

    id = models.BigIntegerField(primary_key=True)
    user_account = models.ForeignKey(BotAccount, models.CASCADE, 'submissions')
    file = models.FileField(upload_to=functions.code_submission_file_name)
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.PENDING)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f'{self.user_account} : {self.id}'


__all__ = ('BotAccount',)
