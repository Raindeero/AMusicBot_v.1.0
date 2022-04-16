import threading
import typing
from datetime import datetime, timedelta

from aiogram import types


class AiogramTTLCache:
    _rlock = threading.RLock()

    def __init__(self, **ttl):
        self.ttl = ttl
        self.cache = {}
        self.default = datetime(2000, 1, 1)

    def get(self, *,
            message: types.Message = None,
            chat: typing.Union[str, int] = None,
            user: typing.Union[str, int] = None):
        with AiogramTTLCache._rlock:
            if message is not None:
                chat, user = message.chat.id, message.from_user.id

            chat, user = self.check_input(chat=chat, user=user)
            ttl = self.cache.get(chat, {}).get(user, self.default)
            if datetime.now() < ttl:
                return True

            self.cache.get(chat, {}).pop(user, None)

            return False

    def set(self, *,
            message: types.Message = None,
            chat: typing.Union[str, int] = None,
            user: typing.Union[str, int] = None, **ttl):
        with AiogramTTLCache._rlock:
            if message is not None:
                chat, user = message.chat.id, message.from_user.id

            chat, user = self.check_input(chat=chat, user=user)
            delta_ttl = ttl or self.ttl
            if not delta_ttl:
                raise Exception("where ttl?????")

            time = datetime.now() + timedelta(**delta_ttl)
            self.cache.setdefault(chat, {}).setdefault(user, time)

    def left(self, *,
             message: types.Message = None,
             chat: typing.Union[str, int] = None,
             user: typing.Union[str, int] = None) -> timedelta:
        with AiogramTTLCache._rlock:
            if message is not None:
                chat, user = message.chat.id, message.from_user.id

            chat, user = self.check_input(chat=chat, user=user)
            if self.get(chat=chat, user=user):
                return self.cache.get(chat).get(user) - datetime.now()

            else:
                return timedelta()

    @staticmethod
    def check_input(chat: typing.Union[str, int], user: typing.Union[str, int]):
        if chat is None and user is None:
            raise ValueError('`user` or `chat` parameter is required but no one is provided!')

        if user is None and chat is not None:
            user = chat

        elif user is not None and chat is None:
            chat = user

        return str(chat), str(user)
