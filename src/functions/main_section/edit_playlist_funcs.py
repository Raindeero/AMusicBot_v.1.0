from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from resources.tools.database import SQLite3Database
from resources.tools.keyboards import InlineKeyboard, Call
from resources.tools.states import StateOn
from src.content import GET_PLAYLIST_MUSIC_BY_PLAYLIST_ID_REQ, DELETE_PLAYLIST_REQ, DELETE_PLAYLIST_CONTENT_REQ, \
    RENAME_PLAYLIST_REQ, GET_PLAYLISTS_BY_NAME_REQ
from src.functions.main_section.playlist_func import playlist_buttons_func, callback_edit_text, get_tracks, \
    get_playlist, error_message, send_edit_text


async def editing_playlist_func(call: CallbackQuery, state: FSMContext, db: SQLite3Database):
    await call.answer(cache_time=1)

    pl, arg, pl_id = call.data.split(':')

    playlist = await get_playlist(db, int(pl_id))

    if not playlist:
        await state.finish()
        return

    if arg in ['name', 'add', 'rem', 'del']:
        kb = InlineKeyboard(Call('❌Отменить', f'pl:edit:{pl_id}'))
        await state.update_data(mid=call.message.message_id, pl_id=pl_id)

        # Rename
        if arg == 'name':
            txt = '<b>Введите новое название для плейлиста:</b>'
            await StateOn.RenamePlaylistNameInput.set()

        # Add
        elif arg == 'add':
            '''
            if len(db.fetch(GET_PLAYLIST_MUSIC_BY_PLAYLIST_ID_REQ, [playlist.playlist_id])) >= 10:
                await call.answer('Увы, но в плейлисте не может быть больше 10 песен!', cache_time=1)
                return
            '''


            txt = '<b>Пришлите песню для добавления:</b>'
            await StateOn.AddMusicToPlaylistInput.set()

        # Remove
        elif arg == 'rem':
            tracks = await get_tracks(db, int(pl_id))
            if not tracks:
                await call.answer('В плейлисте нет песен для удаления!', cache_time=1)
                return

            '''
            if len(tracks) >= 10:
                await call.answer('Увы, но в плейлисте не может быть больше 10 песен!', cache_time=1)
                return
            '''

            txt = '<b>Введите номер песни в плейлисте для удаления:</b>\n'
            txt += '\n'.join([f'{i}) {t.title}' for i, t in enumerate(tracks, start=1)])
            await StateOn.RemMusicFromPlaylistInput.set()

        # Delete playlist
        elif arg == 'del':
            kb = InlineKeyboard(Call('✅', f'epl:agr_del:{pl_id}'), Call('❌', f'pl:edit:{pl_id}'))
            txt = '<b>Вы правда хотите удалить плейлист?</b>'
            await StateOn.DeletePlaylistAgree.set()

        else:
            return

    elif arg in ['new_name', 'agr_del']:
        data = await state.get_data()
        print(data)
        if arg == 'new_name':
            db.execute(RENAME_PLAYLIST_REQ, [data["playlist_name"], int(pl_id), call.from_user.id])
            call.data = f'pl:edit:{pl_id}'

        elif arg == 'agr_del':
            db.execute(DELETE_PLAYLIST_REQ, [int(pl_id)])
            db.execute(DELETE_PLAYLIST_CONTENT_REQ, [int(pl_id)])

            call.data = f'pl:switch:1'

        else:
            return

        await state.reset_data()

        await playlist_buttons_func(call, state, db)
        return

    else:
        return

    await callback_edit_text(call, txt, kb)


async def rename_playlist_input(mes: Message, state: FSMContext, db: SQLite3Database):
    await mes.delete()
    name = mes.text

    if len(name) > 30:
        await error_message(mes, 'Слишком длинное имя!')
        return

    if db.fetch(GET_PLAYLISTS_BY_NAME_REQ, [name, mes.from_user.id]):
        await error_message(mes, 'Плейлист с данным именем уже существует!')
        return

    await state.update_data(playlist_name=name)

    async with state.proxy() as data:
        txt = f'<b>Изменить название плейлиста:</b> {name}'
        kb = InlineKeyboard(Call('✅', f'epl:new_name:{data["pl_id"]}'), Call('❌', f'pl:edit:{data["pl_id"]}'))

        await send_edit_text(mes, txt, data['mid'], kb)
        await StateOn.RenamePlaylistNameAgree.set()
