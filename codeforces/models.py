from django.db import models
from common import fields as common_fields
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator


class UserAccount(models.Model):
    handle = common_fields.ICharField(max_length=64, unique=True)
    clear_password = models.CharField(validators=(MinLengthValidator(5),), max_length=32)
    email = common_fields.IEmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f'{self.email} : {self.handle}'


class Tag(models.Model):
    name = common_fields.ICharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-id',)


class ProblemSet(models.Model):
    name = models.CharField(max_length=64)
    short_name = common_fields.ICharField(max_length=16, unique=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f'{self.short_name} : {self.name}'


class Contest(models.Model):
    class Type(models.IntegerChoices):
        CF = 1, 'CF'
        IOI = 2, 'IOI'
        ICPC = 3, 'ICPC'

    class Phase(models.IntegerChoices):
        BEFORE = 1, 'Before'
        CODING = 2, 'Coding'
        PENDING_SYSTEM_TEST = 3, 'Pending System Test'
        SYSTEM_TEST = 4, 'System Test'
        FINISHED = 5, 'Finished'

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    type = models.PositiveSmallIntegerField(choices=Type.choices)
    phase = models.PositiveSmallIntegerField(choices=Phase.choices)
    is_frozen = models.BooleanField()
    difficulty = models.PositiveSmallIntegerField(validators=(MinValueValidator(1), MaxValueValidator(5)))
    kind = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f'{self.id} : {self.name}'


class Problem(models.Model):
    class Type(models.IntegerChoices):
        PROGRAMMING = 1, 'Programming'
        QUESTION = 2, 'Question'

    contest = models.ForeignKey(Contest, models.CASCADE, 'problems', blank=True, null=True)
    problem_set = models.ForeignKey(ProblemSet, models.CASCADE, 'problems', blank=True, null=True)
    index = models.CharField(max_length=8)
    name = models.CharField(max_length=64)
    type = models.PositiveSmallIntegerField(choices=Type.choices)
    points = models.FloatField(blank=True, null=True)
    rating = models.PositiveSmallIntegerField()
    tags = models.ManyToManyField(Tag, 'problems')

    class Meta:
        ordering = ('-id',)
        constraints = (
            models.CheckConstraint(
                check=models.Q(contest__isnull=False) | models.Q(problem_set__isnull=False), name='valid_problem'
            ),
            models.UniqueConstraint(
                fields=('contest', 'index'), name='unique_contest_problem', condition=models.Q(contest__isnull=False)
            ),
            models.UniqueConstraint(
                fields=('problem_set', 'index'),
                name='unique_problem_set_problem',
                condition=models.Q(problem_set__isnull=False)
            )
        )

    def __str__(self):
        return f'{self.contest or self.problem_set} : {self.name}'


__all__ = ('UserAccount', 'Tag', 'ProblemSet', 'Contest', 'Problem')
