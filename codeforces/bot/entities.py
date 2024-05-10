from aiohttp import ClientSession
from . import urls
from codeforces import models
from common.bot import exceptions as common_exceptions, entities as common_entities
from bs4 import BeautifulSoup
from django.db import IntegrityError
from django.core.management import BaseCommand


class CFBot(common_entities.Bot):
    _logout_url: str | None

    def __init__(self, account: models.CFBotAccount, session: ClientSession, command: BaseCommand):
        super().__init__(account, session, command)
        self._logout_url = None

    async def login(self):
        await super().login()
        self._check_page_load(response := await self._session.get(urls.LOGIN_URL))
        response = await self._session.post(urls.LOGIN_URL, data={
            'csrf_token': self._extract_csrf_token(await self._generate_soup(response)),
            'action': 'enter',
            'handleOrEmail': self._account.handle,
            'password': self._account.clear_password,
            'remember': 'on'
        })
        self._check_page_load(response)
        self._logout_url = urls.BASE_URL + self._check_authentication(await self._generate_soup(response))
        self._logged_in()

    async def logout(self):
        if self._status != CFBot.Status.READY:
            raise common_exceptions.InvalidBotStateException(CFBot.Status.READY, self._status)
        self._check_page_load(await self._session.get(self._logout_url))
        await super().logout()

    def _extract_csrf_token(self, soup: BeautifulSoup):
        if csrf_token := soup.find('input', {'name': 'csrf_token'}):
            return csrf_token['value']
        raise common_exceptions.CSRFTokenNotFound(soup)

    def _check_authentication(self, soup: BeautifulSoup):
        if logout_link := soup.find('a', string='Logout'):
            return logout_link['href']
        raise common_exceptions.AuthenticationFailed(self._account)

    @common_entities.Bot._retry_authentication
    async def _load_submit_page(self, problem: models.Problem) -> tuple[str, BeautifulSoup]:
        self._check_authentication(soup := await self._generate_soup(
            await self._session.get(url := urls.generate_problem_set_submit_url(
                problem.problem_set
            ) if problem.problem_set else urls.CONTEST_SUBMIT_URL, max_redirects=1)
        ))
        return url, soup

    @common_entities.Bot._retry_authentication
    async def _submit_code_page(self, url: str, soup: BeautifulSoup, submission: models.CFCodeSubmission):
        data = {
            'csrf_token': (csrf_token := self._extract_csrf_token(soup)),
            'action': 'submitSolutionFormSubmitted',
            'submittedProblemCode': f'{submission.problem.contest.id}{submission.problem.index}'
            if submission.problem.contest else str(submission.problem.index),
            'programTypeId': str(submission.programming_language.website_id),
            'sourceFile': submission.file.open()
        }
        self._check_authentication(
            soup := await self._generate_soup(await self._session.post(url + f'?csrf_token={csrf_token}', data=data))
        )
        return soup

    async def _submit_code(self, submission: models.CFCodeSubmission):
        soup = await self._submit_code_page(*await self._load_submit_page(submission.problem), submission)
        if submission_id := soup.find(class_='view-source'):
            submission.submission_id = submission_id['submissionid']
            submission.status = models.CFCodeSubmission.Status.SUBMITTED
            try:
                await submission.asave(update_fields=('status', 'submission_id'))
                return
            except IntegrityError:
                submission.submission_id = None
        submission.status = models.CFCodeSubmission.Status.FAILED
        await submission.asave(update_fields=('status',))

    def _get_submissions(self):
        return models.CFCodeSubmission.objects.filter(
            bot_account=self._account, status=models.CFCodeSubmission.Status.IN_PROGRESS
        ).select_related('problem__contest', 'problem__problem_set', 'programming_language')


class CFManager(common_entities.Manager):
    def _get_active_accounts(self):
        return models.CFBotAccount.objects.filter(status=models.CFBotAccount.Status.ACTIVE)

    async def _run_bot(self, account: models.CFBotAccount):
        async with ClientSession() as session:
            async with CFBot(account, session, self._command) as bot:
                try:
                    await bot.run()
                except common_exceptions.BotException:
                    pass

    def _get_submissions(self):
        return models.CFCodeSubmission.objects


__all__ = ('CFBot', 'CFManager')
