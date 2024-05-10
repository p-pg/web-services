from django.core.management.base import BaseCommand
from abc import ABC, abstractmethod
import asyncio


class BotCommand(ABC, BaseCommand):
    @abstractmethod
    async def run_manager(self):
        pass

    def handle(self, *args, **options):
        asyncio.run(self.run_manager())


__all__ = ('BotCommand',)
