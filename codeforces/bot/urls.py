from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codeforces.models import ProblemSet

BASE_URL = 'https://codeforces.com'
LOGIN_URL = f'{BASE_URL}/enter'
PROBLEM_SET_URL = f'{BASE_URL}/problemset'
CONTEST_SUBMIT_URL = f'{PROBLEM_SET_URL}/submit'


def generate_problem_set_submit_url(problem_set: 'ProblemSet'):
    return f'{PROBLEM_SET_URL}s/{problem_set.short_name}/submit'


__all__ = ('BASE_URL', 'LOGIN_URL', 'PROBLEM_SET_URL', 'CONTEST_SUBMIT_URL', 'generate_problem_set_submit_url')
