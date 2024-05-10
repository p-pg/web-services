from common.commands import BotCommand
from codeforces.bot.entities import CFManager
import asyncio


class Command(BotCommand):
    async def run_manager(self):
        manager = CFManager(asyncio.get_running_loop(), self)
        await manager.run()


__all__ = ('Command',)
