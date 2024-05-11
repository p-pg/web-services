from django.db.models import IntegerChoices
from django.utils import timezone
from aiohttp import ClientSession, ClientResponse
from abc import ABC, abstractmethod
from . import exceptions
from functools import wraps
from aiohttp import TooManyRedirects
from common import models
from bs4 import BeautifulSoup
import asyncio
from django.core.management import BaseCommand


class Bot(ABC):
    class Status(IntegerChoices):
        BEFORE_AUTHENTICATION = 1, 'Before Authentication'
        AUTHENTICATING = 2, 'Authenticating'
        AUTHENTICATION_FAILED = 3, 'Authentication Failed'
        READY = 4, 'Ready'
        WORKING = 5, 'Working'
        LOGGED_OUT = 6, 'Logged Out'

    active_accounts: dict[int, models.BotAccount] = dict()
    inactive_accounts: set[int] = set()
    _account: models.BotAccount
    _status: Status
    _session: ClientSession
    _command: BaseCommand

    def __init__(self, account: models.BotAccount, session: ClientSession, command: BaseCommand):
        self._account = account
        self._status = Bot.Status.BEFORE_AUTHENTICATION
        self._session = session
        self._command = command

    async def __aenter__(self):
        self._command.stdout.write(self._command.style.SUCCESS(f'{self._account}: Started.'))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._command.stderr.write(self._command.style.NOTICE(f'{self._account}: Stopped!'))
        self.inactive_accounts.discard(self._account.id)
        match exc_type:
            case exceptions.AuthenticationFailed:
                self._account.status = models.BotAccount.Status.AUTHENTICATION_FAILED
                await self._account.asave(update_fields=('status',))
                del self.active_accounts[self._account.id]
                return True
            case exceptions.InactiveAccount:
                del self.active_accounts[self._account.id]
                return True
        del self.active_accounts[self._account.id]

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
                self._logged_out()
                await self.login()
                try:
                    return await (method(self, *args, **kwargs)
                                  if isinstance(e, TooManyRedirects) and len(e.history) == 1
                                  else self._session.get(e.history[-1].url))
                except TooManyRedirects as e:
                    raise exceptions.PageLoadFailed(str(e.request_info.url))

        return func

    def _logged_out(self):
        self._status = Bot.Status.BEFORE_AUTHENTICATION
        self._command.stdout.write(self._command.style.NOTICE(f'{self._account}: Logged Out!'))

    def _logged_in(self):
        self._status = Bot.Status.READY
        self._command.stdout.write(self._command.style.SUCCESS(f'{self._account}: Logged In.'))

    async def login(self):
        if self._status != Bot.Status.BEFORE_AUTHENTICATION:
            raise exceptions.InvalidBotStateException(Bot.Status.BEFORE_AUTHENTICATION, self._status)

    @abstractmethod
    @_retry_authentication
    async def _load_submit_page(self) -> tuple[str, BeautifulSoup]:
        pass

    @abstractmethod
    @_retry_authentication
    async def _submit_code_page(self, url: str, soup: BeautifulSoup, submission: models.CodeSubmission):
        pass

    @abstractmethod
    async def _submit_code(self, submission: models.CodeSubmission):
        pass

    async def logout(self):
        self._status = Bot.Status.LOGGED_OUT

    @abstractmethod
    def _extract_csrf_token(self, soup: BeautifulSoup):
        pass

    async def _generate_soup(self, response: ClientResponse):
        self._check_page_load(response)
        return BeautifulSoup(await response.read(), 'html.parser')

    async def _check_account(self):
        try:
            await self._account.arefresh_from_db()
        except models.BotAccount.DoesNotExist:
            raise exceptions.InactiveAccount(self._account)
        if self._account.status != models.BotAccount.Status.ACTIVE:
            raise exceptions.InactiveAccount(self._account)

    @abstractmethod
    def _get_submissions(self):
        pass

    @abstractmethod
    async def _get_submissions_result(self):
        pass

    async def run(self):
        await self.login()
        while self._account.id not in self.inactive_accounts:
            async for submission in self._get_submissions():
                await self._submit_code(submission)
                await asyncio.sleep(1)
            await self._get_submissions_result()
            await asyncio.sleep(5)
            await self._check_account()


class Manager(ABC):
    _tasks: set[asyncio.Task]
    _event_loop: asyncio.AbstractEventLoop
    _command: BaseCommand

    def __init__(self, event_loop: asyncio.AbstractEventLoop, command: BaseCommand):
        self._tasks = set()
        self._event_loop = event_loop
        self._command = command

    @abstractmethod
    def _get_active_accounts(self):
        pass

    @abstractmethod
    async def _run_bot(self, account: models.BotAccount):
        pass

    @abstractmethod
    def _get_submissions(self):
        pass

    async def _assign_tasks(self):
        await self._get_submissions().exclude(bot_account__in=Bot.active_accounts).filter(
            status=models.CodeSubmission.Status.IN_PROGRESS
        ).aupdate(status=models.CodeSubmission.Status.PENDING, bot_account=None)
        if not (active_accounts := [active_account async for active_account in self._get_active_accounts()]):
            return
        current_index = 0
        submission: models.CodeSubmission
        async for submission in self._get_submissions().filter(status=models.CodeSubmission.Status.PENDING):
            active_account: models.BotAccount = active_accounts[current_index]
            submission.bot_account = active_account
            submission.status = models.CodeSubmission.Status.IN_PROGRESS
            await submission.asave(update_fields=('bot_account', 'status'))
            active_account.last_assignment = timezone.now()
            await active_account.asave(update_fields=('last_assignment',))
            if current_index == len(active_accounts) - 1:
                current_index = 0
            else:
                current_index += 1

    async def run(self):
        while True:
            active_dict = {active_account.id: active_account async for active_account in self._get_active_accounts()}
            new_accounts = list()
            for key, account in active_dict.items():
                if key not in Bot.active_accounts:
                    Bot.active_accounts[key] = account
                    new_accounts.append(account)
            for new_account in new_accounts:
                task = self._event_loop.create_task(self._run_bot(new_account))
                task.add_done_callback(self._tasks.remove)
                self._tasks.add(task)
            await self._assign_tasks()
            await asyncio.sleep(5)


__all__ = ('Bot', 'Manager')
