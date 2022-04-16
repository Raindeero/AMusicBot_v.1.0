from logging import info

from aiogram import Dispatcher

from .search_handlers import register_example_handlers


async def run_handlers(dp: Dispatcher):
    info('▻ Installing a handlers...')

    await register_example_handlers(dp)
    info('▻ EXAMPLE handlers was successful installed!')
