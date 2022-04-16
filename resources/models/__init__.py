import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import config


# Here you can create tool instances if you needed.

# Loop
from resources.tools import database

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# MemoryStorage
storage = MemoryStorage()


# Bots
bot = Bot(token=config.BOT_TOKEN, loop=loop, parse_mode=config.PARSE_MODE)

# Dispatchers
dp = Dispatcher(bot, storage=storage, loop=loop)


# Comment if you no need to user PostgreSQL Database
db = database.SQLite3Database(config.SQLITE_DB_PATH)
