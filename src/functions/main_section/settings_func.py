from aiogram.types import CallbackQuery, Message


async def none_callback(call: CallbackQuery):
    await call.answer(cache_time=1)


async def close_callback(call: CallbackQuery):
    await call.message.delete()


async def info_func(mes: Message):
    await mes.answer(mes)