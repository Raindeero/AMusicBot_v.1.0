from logging import info

from aiogram import executor, Dispatcher

from config import config
from resources.models import dp, loop, db
from resources.tools import bot_logging

from resources.tools.middleware import installing_middlewares
from src.handlers import run_handlers


async def startup_func(dp: Dispatcher):
    info('= = = Starting a bot! = = =')
    info(f'Current version: {config.CURRENT_VERSION}')

    # Skip updates
    await dp.skip_updates()

    # Handlers
    await run_handlers(dp)

    info('= = = = = = = = =')

    # Connecting to databases
    db.connect()

    info('= = = = = = = = =')

    # Middlewares
    await installing_middlewares(dp)

    info('= = = Bot is working! = = =')


if __name__ == '__main__':
    # Set Logging
    bot_logging.set_logging(config.debug)

    executor.start_polling(dp, loop=loop, on_startup=startup_func)
