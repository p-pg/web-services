from codeforces.models import CFBotAccount
from aiohttp import ClientSession, ClientResponse
from . import urls
from common.bot import exceptions as common_exceptions, entities as common_entities
from bs4 import BeautifulSoup


class CFBot(common_entities.Bot):

    _logout_url: str | None

    def __init__(self, account: CFBotAccount, session: ClientSession):
        super().__init__(account, session)
        self._logout_url = None

    async def login(self):
        if self._status != CFBot.Status.BEFORE_AUTHENTICATION:
            raise common_exceptions.InvalidBotStateException(CFBot.Status.BEFORE_AUTHENTICATION, self._status)
        response = await self._session.post(urls.LOGIN_URL, data={
            'csrf_token': await self.extract_csrf_token(await self._session.get(urls.LOGIN_URL)),
            'action': 'enter',
            'handleOrEmail': self._account.handle,
            'password': self._account.clear_password,
            'remember': 'on'
        })
        self.check_page_load(response)
        self._logout_url = await self.check_authentication(response)
        await super().login()

    async def logout(self):
        if self._status != CFBot.Status.READY:
            raise common_exceptions.InvalidBotStateException(CFBot.Status.READY, self._status)
        self.check_page_load(await self._session.get(self._logout_url))
        await super().logout()

    async def extract_csrf_token(self, response: ClientResponse):
        await super().extract_csrf_token(response)
        soup = BeautifulSoup(await response.content.read(), 'html.parser')
        if csrf_token := soup.find('input', {'name': 'csrf_token'}):
            return csrf_token['value']
        raise common_exceptions.CSRFTokenNotFound(response)

    async def check_authentication(self, response: ClientResponse):
        await super().check_authentication(response)
        soup = BeautifulSoup(await response.content.read(), 'html.parser')
        if logout_link := soup.find('a', string='Logout'):
            return urls.BASE_URL + logout_link['href']
        raise common_exceptions.AuthenticationFailed(self._account)


__all__ = ('CFBot',)
