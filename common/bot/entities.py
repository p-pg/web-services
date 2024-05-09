from django.db.models import IntegerChoices
from aiohttp import ClientSession, ClientResponse
from abc import ABC, abstractmethod
from . import exceptions
from functools import wraps
from aiohttp import TooManyRedirects
from common import models
from bs4 import BeautifulSoup


class Bot(ABC):
    class Status(IntegerChoices):
        BEFORE_AUTHENTICATION = 1, 'Before Authentication'
        AUTHENTICATING = 2, 'Authenticating'
        AUTHENTICATION_FAILED = 3, 'Authentication Failed'
        READY = 4, 'Ready'
        WORKING = 5, 'Working'
        LOGGED_OUT = 6, 'Logged Out'

    _active_accounts = set()
    _inactive_accounts = set()
    _account: models.BotAccount
    _status: Status
    _session: ClientSession

    def __init__(self, account: models.BotAccount, session: ClientSession):
        self._account = account
        self._status = Bot.Status.BEFORE_AUTHENTICATION
        self._session = session

    async def __aenter__(self):
        self._active_accounts.add(self._account.id)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type == exceptions.AuthenticationFailed:
            self._account.status = models.BotAccount.Status.AUTHENTICATION_FAILED
            await self._account.asave(update_fields=('status',))
            self._active_accounts.remove(self._account.id)
            return True
        self._active_accounts.remove(self._account.id)

    def _check_page_load(self, response: ClientResponse):
        if response.status != 200:
            raise exceptions.PageLoadFailed(str(response.url))

    @abstractmethod
    def _check_authentication(self, soup: BeautifulSoup):
        pass

    @staticmethod
    def _retry_authentication(method):
        @wraps(method)
        async def func(self, *args, **kwargs):
            try:
                return await method(self, *args, **kwargs)
            except (TooManyRedirects, exceptions.AuthenticationFailed) as e:
                await self.login()
                try:
                    return await (method(self, *args, **kwargs)
                                  if isinstance(e, TooManyRedirects) and len(e.history) == 1
                                  else self._session.get(e.history[-1].url))
                except TooManyRedirects as e:
                    raise exceptions.PageLoadFailed(str(e.request_info.url))

        return func

    async def login(self):
        self._status = Bot.Status.READY

    @abstractmethod
    @_retry_authentication
    async def _load_submit_page(self) -> tuple[str, BeautifulSoup]:
        pass

    @abstractmethod
    @_retry_authentication
    async def _submit_code_page(self, url: str, soup: BeautifulSoup, submission: models.CodeSubmission):
        pass

    async def submit_code(self, submission: models.CodeSubmission):
        submission.user_account = self._account
        submission.status = models.CodeSubmission.Status.IN_PROGRESS
        await submission.asave(update_fields=('status', 'user_account'))

    async def logout(self):
        self._status = Bot.Status.LOGGED_OUT

    @abstractmethod
    def _extract_csrf_token(self, soup: BeautifulSoup):
        pass

    async def _generate_soup(self, response: ClientResponse):
        self._check_page_load(response)
        return BeautifulSoup(await response.read(), 'html.parser')

    async def check_account(self):
        try:
            await self._account.arefresh_from_db()
        except models.BotAccount.DoesNotExist:
            raise exceptions.InactiveAccountException(self._account)
        if self._account.status != models.BotAccount.Status.ACTIVE:
            raise exceptions.InactiveAccountException(self._account)


__all__ = ('Bot',)
