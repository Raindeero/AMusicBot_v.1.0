from logging import info

from aiogram import Dispatcher
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineQuery

from resources.models import db
from resources.tools.middleware.AiogramTTLCache import AiogramTTLCache


class Middleware(BaseMiddleware):
    def __init__(self, db):
        self.db = db
        super(Middleware, self).__init__()

    async def on_process_message(self, message: Message, data: dict):
        data['db'] = self.db

    async def on_process_callback_query(self, callback_query: CallbackQuery, data: dict):
        data['db'] = self.db

    async def on_process_inline_query(self, inline_query: InlineQuery, data: dict):
        data['db'] = self.db


class ThrottleMiddleware(BaseMiddleware):
    """ Make a throttling """
    def __init__(self, seconds: int = 1):
        self.cache = AiogramTTLCache(seconds=seconds)

        super(ThrottleMiddleware, self).__init__()

    async def on_process_message(self, message: Message, data: dict):
        if not self.cache.get(message=message):
            self.cache.set(message=message)
            return

        else:
            # cache.set(message, seconds=int(cache.left(message).total_seconds() * 2))
            # await message.answer(f"flood control wait {self.cache.left(message=message)} sec.")
            raise CancelHandler


async def installing_middlewares(dp: Dispatcher):
    dp.middleware.setup(ThrottleMiddleware())
    info('▻ ThrottleMiddleware is setup!')

    dp.middleware.setup(Middleware(db))
    info('▻ Middleware is setup!')
