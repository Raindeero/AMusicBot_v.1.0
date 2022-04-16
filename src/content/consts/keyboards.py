from resources.tools.keyboards import InlineKeyboard, Call


async def pl_edit_kb(pl_id: int):
    return InlineKeyboard(
        Call('📝Изм. название', f'epl:name:{pl_id}'),
        Call('🎶Добавить', f'epl:add:{pl_id}'), Call('🎶Убрать', f'epl:rem:{pl_id}'),
        Call('❌Удалить плейлист', f'epl:del:{pl_id}'), Call('Назад', 'pl:switch:1'), row_width=2
    )