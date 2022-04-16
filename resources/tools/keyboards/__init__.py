from aiogram.types import InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB, ReplyKeyboardMarkup as RKM


__all__ = ['Call', 'Url', 'InlineKeyboard', 'ReplyKeyboard']


# Button Types
def Call(*args):
    return dict(zip(('text', 'callback_data'), args))


def Url(*args):
    return dict(zip(('text', 'url'), args))


# Custom Inline Keyboard Constructor
def InlineKeyboard(*args, row_width: int = 5):
    return IKM(row_width=row_width).add(*(IKB(**l) for l in args))


# Custom Reply Keyboard Constructor (While nothing special)
def ReplyKeyboard(*args: str, row_width: int = 3):
    return RKM(resize_keyboard=True, selective=True, row_width=row_width).add(*args)
