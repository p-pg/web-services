from typing import TYPE_CHECKING
from aiohttp import ClientResponse
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from common.bot.entities import Bot
    from common.models import BotAccount


class BotException(Exception):
    def __str__(self):
        return 'Codeforces Bot Exception!'


class InvalidBotStateException(BotException):
    valid_state: 'Bot.Status'
    current_state: 'Bot.Status'

    def __init__(self, valid_state: 'Bot.Status', current_state: 'Bot.Status'):
        assert valid_state != current_state, 'Valid State and Current State must be different!'

    def __str__(self):
        return (f'Bot must be in "{self.valid_state.name}" state, '
                f'but it\'s in "{self.current_state.name}" state instead!')


class PageLoadFailed(BotException):
    url: str

    def __init__(self, url: str):
        self.url = url

    def __str__(self):
        return f'Loading the page "{self.url}" failed!'


class SoupException(BotException):
    soup: BeautifulSoup

    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def __str__(self):
        return 'Soup Exception!'


class CSRFTokenNotFound(SoupException):
    def __str__(self):
        return 'CSRF Token was not found!'


class BotAccountException(BotException):
    account: 'BotAccount'

    def __init__(self, account: 'BotAccount'):
        self.account = account

    def __str__(self):
        return f'Account Exception on: "{self.account}"!'


class AuthenticationFailed(BotAccountException):
    def __str__(self):
        return f'Authentication failed for: "{self.account.handle}"'


class InactiveAccountException(BotAccountException):
    def __str__(self):
        return f'Account "{self.account}" is inactive!'


__all__ = (
    'BotException',
    'InvalidBotStateException',
    'PageLoadFailed',
    'SoupException',
    'CSRFTokenNotFound',
    'BotAccountException',
    'AuthenticationFailed',
    'InactiveAccountException'
)
