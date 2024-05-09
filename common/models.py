from django.db import models
from . import fields, functions
from django.core.validators import MinLengthValidator
from django.utils import timezone


class BotAccount(models.Model):
    class Status(models.IntegerChoices):
        ACTIVE = 1, 'Active'
        AUTHENTICATION_FAILED = 2, 'Authentication Failed'
        INACTIVE = 3, 'Inactive'

    handle = fields.ICharField(max_length=64, unique=True)
    clear_password = models.CharField(validators=(MinLengthValidator(5),), max_length=32)
    email = fields.IEmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=timezone.now)
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f'{self.email} : {self.handle}'


class CodeSubmission(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 1, 'Pending'
        IN_PROGRESS = 2, 'In Progress'
        FAILED = 3, 'Failed'
        SUBMITTED = 4, 'Submitted'

    user_account = models.ForeignKey(BotAccount, models.CASCADE, 'submissions', blank=True, null=True)
    file = models.FileField(upload_to=functions.code_submission_file_name)
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.PENDING)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    submission_id = models.BigIntegerField(unique=True, blank=True, null=True)

    class Meta:
        ordering = ('-id',)
        constraints = (models.CheckConstraint(
            check=models.Q(status=4, submission_id__isnull=False) | (
                ~models.Q(status=4) & models.Q(submission_id__isnull=True)
            ),
            name='valid_submitted_code'
        ), models.CheckConstraint(check=(~models.Q(status=1) & models.Q(user_account__isnull=False)) |
                                  models.Q(status=1, user_account__isnull=True), name='valid_assigned_code'))

    def __str__(self):
        return f'{self.user_account} : {self.id}'


__all__ = ('BotAccount',)
