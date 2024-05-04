from django.db.models import IntegerChoices
from common.models import BotAccount
from aiohttp import ClientSession, ClientResponse
from abc import ABC
from . import exceptions


class Bot(ABC):
    class Status(IntegerChoices):
        BEFORE_AUTHENTICATION = 1, 'Before Authentication'
        AUTHENTICATING = 2, 'Authenticating'
        AUTHENTICATION_FAILED = 3, 'Authentication Failed'
        READY = 4, 'Ready'
        WORKING = 5, 'Working'
        LOGGED_OUT = 6, 'Logged Out'

    _account: BotAccount
    _status: Status
    _session: ClientSession

    def __init__(self, account: BotAccount, session: ClientSession):
        self._account = account
        self._status = Bot.Status.BEFORE_AUTHENTICATION
        self._session = session

    async def __aenter__(self):
        self._account.status = BotAccount.Status.IN_USE
        await self._account.asave(update_fields=('status',))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type == exceptions.AuthenticationFailed:
            self._account.status = BotAccount.Status.AUTHENTICATION_FAILED
            await self._account.asave(update_fields=('status',))
            return True
        self._account.status = BotAccount.Status.READY
        await self._account.asave(update_fields=('status',))

    def check_page_load(self, response: ClientResponse):
        if response.status != 200:
            raise exceptions.PageLoadFailed(str(response.url))

    async def check_authentication(self, response: ClientResponse):
        self.check_page_load(response)

    async def login(self):
        self._status = Bot.Status.READY

    async def logout(self):
        self._status = Bot.Status.LOGGED_OUT

    async def extract_csrf_token(self, response: ClientResponse):
        self.check_page_load(response)


__all__ = ('Bot',)
