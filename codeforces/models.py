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


class Submission(models.Model):
    class ProgrammingLanguage(models.IntegerChoices):
        PYTHON = 1, 'Python'
        CPP = 2, 'C++'

    class Verdict(models.IntegerChoices):
        FAILED = 1, 'Failed'
        PARTIAL = 2, 'Partial'
        COMPILATION_ERROR = 3, 'Compilation Error'
        RUNTIME_ERROR = 4, 'Runtime Error'
        WRONG_ANSWER = 5, 'Wrong Answer'
        PRESENTATION_ERROR = 6, 'Presentation Error'
        TIME_LIMIT_EXCEEDED = 7, 'Time Limit Exceeded'
        MEMORY_LIMIT_EXCEEDED = 8, 'Memory Limit Exceeded'
        IDLENESS_LIMIT_EXCEEDED = 9, 'Idleness Limit Exceeded'
        SECURITY_VIOLATED = 10, 'Security Violated'
        CRASHED = 11, 'Crashed'
        INPUT_PREPARATION_CRASHED = 12, 'Input Preparation Crashed'
        CHALLENGED = 13, 'Challenged'
        SKIPPED = 14, 'Skipped'
        TESTING = 15, 'Testing'
        REJECTED = 16, 'Rejected'

    class TestSet(models.IntegerChoices):
        SAMPLES = 1, 'Samples'
        PRETESTS = 2, 'Pretests'
        TESTS = 3, 'Tests'
        CHALLENGES = 4, 'Challenges'
        TESTS_1 = 5, 'Tests 1'
        TESTS_2 = 6, 'Tests 2'
        TESTS_3 = 7, 'Tests 3'
        TESTS_4 = 8, 'Tests 4'
        TESTS_5 = 9, 'Tests 5'
        TESTS_6 = 10, 'Tests 6'
        TESTS_7 = 11, 'Tests 7'
        TESTS_8 = 12, 'Tests 8'
        TESTS_9 = 13, 'Tests 9'
        TESTS_10 = 14, 'Tests 10'

    id = models.BigIntegerField(primary_key=True)
    problem = models.ForeignKey(Problem, models.CASCADE, 'submissions')
    user_account = models.ForeignKey(UserAccount, models.CASCADE, 'submissions')
    programming_language = models.PositiveSmallIntegerField(choices=ProgrammingLanguage.choices)
    verdict = models.PositiveSmallIntegerField(choices=Verdict.choices, blank=True, null=True)
    test_set = models.PositiveSmallIntegerField(choices=TestSet.choices)
    passed_test_count = models.PositiveSmallIntegerField(default=0)
    time_consumed = models.BigIntegerField(help_text='In Milliseconds')
    memory_consumed = models.BigIntegerField(help_text='In Bytes')
    points = models.FloatField(blank=True, null=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f'{self.problem} : {self.user_account}'


__all__ = ('UserAccount', 'Tag', 'ProblemSet', 'Contest', 'Problem', 'Submission')
