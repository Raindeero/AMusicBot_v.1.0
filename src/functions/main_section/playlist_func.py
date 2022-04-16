import asyncio
import traceback
from logging import error
from typing import List

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton as IKB, Message, MediaGroup
from aiogram.utils.exceptions import MessageNotModified

from resources.models.playlists_models import PlaylistData, MusicData
from resources.tools.database import SQLite3Database
from resources.tools.keyboards import InlineKeyboard, Call
from resources.tools.states import StateOn
from src.content import GET_PLAYLISTS_OF_USER_REQ, CREATE_NEW_PLAYLIST_REQ, GET_NEW_PLAYLIST_INFO_REQ, \
    GET_PLAYLIST_INFO_BY_PLAYLIST_ID_REQ, GET_PLAYLIST_MUSIC_BY_PLAYLIST_ID_REQ, GET_PLAYLISTS_BY_NAME_REQ, \
    PLAYLIST_TEXT, ADD_NEW_MUSIC_TO_PLAYLIST_REQ, REM_MUSIC_FROM_PLAYLIST_REQ
from src.content.consts.keyboards import pl_edit_kb


async def add_music_to_playlist(call: CallbackQuery, db: SQLite3Database, state: FSMContext):
    user_playlists = [PlaylistData(*i) for i in db.fetch(GET_PLAYLISTS_OF_USER_REQ, [call.from_user.id])]
    kb = await add_playlist_kb(user_playlists, force=True)

    x = call.message.audio
    await state.update_data(file_id=x.file_id, duration=x.duration, title=x.title)
    await call.message.answer('<b>Выберите плейлист:</b>', reply_markup=kb)


async def playlist_main_func(mes: Message, db: SQLite3Database):
    user_playlists = [PlaylistData(*i) for i in db.fetch(GET_PLAYLISTS_OF_USER_REQ, [mes.from_user.id])]
    kb = await create_playlist_kb(user_playlists)

    try:
        await mes.delete()
    except Exception:
        pass
    await mes.answer('<b>Ваши плейлисты:</b>', reply_markup=kb)


async def playlist_buttons_func(call: CallbackQuery, state: FSMContext, db: SQLite3Database):
    await call.answer(cache_time=1)

    actions = {

        'fpage': {'txt': '<b>Ваши плейлисты:</b>', 'force': False},

        # Стрелочки и Отменить изменение
        'page': {'txt': '<b>Ваши плейлисты:</b>', 'edit_mode': False},

        # Стрелочки в изменении
        'switch': {'txt': '<b>Выберите плейлист для изменения:</b>', 'edit_mode': True},

        # Изменить
        'change': {'txt': '<b>Выберите плейлист для изменения:</b>', 'edit_mode': True}
    }

    pl, arg, page = call.data.split(':')

    if actions.get(arg):
        if pl == 'dpl' and arg == 'page':
            await state.update_data(mid=None, page=None, playlist_name=None)

        user_playlists = [PlaylistData(*i) for i in db.fetch(GET_PLAYLISTS_OF_USER_REQ, [call.from_user.id])]
        kb = await create_playlist_kb(user_playlists, page=int(page), edit_mode=actions[arg]['edit_mode'])
        txt = actions[arg]['txt']

        await state.finish()

    elif arg == 'create':
        kb = InlineKeyboard(Call('❌Отменить', f'dpl:page:{page}'))
        txt = '<b>Введите название для плейлиста:</b>'

        await state.update_data(mid=call.message.message_id, page=page)
        await StateOn.NewPlaylistNameInput.set()

    elif arg == 'edit':
        pl_id = int(page)
        playlist = db.fetch(GET_PLAYLIST_INFO_BY_PLAYLIST_ID_REQ, [pl_id], one_row=True)

        if not playlist:
            await call.answer('Данного плейлиста не существует!')
            await call.message.delete()
            await state.finish()
            return

        playlist = PlaylistData(*playlist)

        tracks = [
            MusicData(*i) for i in db.fetch(GET_PLAYLIST_MUSIC_BY_PLAYLIST_ID_REQ, [playlist.playlist_id])
        ]

        kb = await pl_edit_kb(pl_id)

        titles = '\n'.join([f'{i}) {t.title}' for i, t in enumerate(tracks, start=1)]) if tracks else 'Нет песен'
        txt = PLAYLIST_TEXT.format(**playlist.get_playlist_txt(titles))
        await state.finish()

    elif arg == 'show':
        if pl == 'npl':
            # Если только создали плейлист
            playlist_name = (await state.get_data())['playlist_name']
            db.execute(CREATE_NEW_PLAYLIST_REQ, [call.from_user.id, (await state.get_data())['playlist_name']])

            await state.reset_data()
            await state.finish()

            playlist = db.fetch(
                GET_NEW_PLAYLIST_INFO_REQ, [call.from_user.id, playlist_name], one_row=True
            )

        else:
            # Просто вызов :show:
            pl_id = int(page)
            playlist = db.fetch(GET_PLAYLIST_INFO_BY_PLAYLIST_ID_REQ, [pl_id], one_row=True)

        if not playlist:
            await call.answer('Данного плейлиста не существует!')
            await call.message.delete()
            return

        playlist = PlaylistData(*playlist)
        tracks = await get_tracks(db, playlist.playlist_id)

        if tracks:
            media_group, titles = await media_groups_formatter(tracks), ''

            for i, track in enumerate(tracks, start=1):
                titles += f'{i}) {track.title}\n'

        else:
            media_group, titles = None, 'Нет песен'

        if not tracks:
            await call.message.answer(
                PLAYLIST_TEXT.format(**playlist.get_playlist_txt(titles)),
                reply_markup=InlineKeyboard(Call('Закрыть', 'Close'))
            )

        if media_group:
            for mg in media_group:
                if isinstance(mg, MusicData):
                    await call.message.answer_audio(mg.file_id)
                else:
                    await call.message.answer_media_group(mg)

                await asyncio.sleep(0.3)


        # Возвращаемся обратно в меню
        if pl == 'npl':
            call.data = 'pl:page:1'
            await playlist_buttons_func(call, state, db)
        return

    elif arg == 'force':
        txt = 'Успешно добавлено!'
        kb = None

        data = await state.get_data()
        db.execute(ADD_NEW_MUSIC_TO_PLAYLIST_REQ, [int(page), data['file_id'], data['title'], data['duration']])
        '''
                if len(db.fetch(GET_PLAYLIST_MUSIC_BY_PLAYLIST_ID_REQ, [int(page)])) >= 10:
            await call.answer('Увы, но в плейлисте не может быть больше 10 песен!', cache_time=1)
            return
        '''
    else:
        return

    await callback_edit_text(call, txt, kb)
    await asyncio.sleep(5)
    try:
        await call.message.delete()
    except Exception:
        pass


async def media_groups_formatter(tracks: List[MusicData], sl: int = 10):
    results = []

    for mg in range(len(tracks)//sl+1):
        pool = tracks[mg:mg + sl]
        if len(pool) == 1:
            results.append(pool[0])
            continue

        media_group = MediaGroup()
        [media_group.attach_audio(track.file_id) for track in tracks[sl * mg:sl * (mg+1)]]
        results.append(media_group)

    return results


async def new_playlist_name_input_func(mes: Message, state: FSMContext, db: SQLite3Database):
    await mes.delete()
    name = mes.text

    if len(name) > 20:
        try:
            m = await mes.answer('Слишком длинное имя!')
            await asyncio.sleep(3)
            await m.delete()

        except Exception:
            error('Message Deleting:\n' + traceback.format_exc())
            pass

        return

    if db.fetch(GET_PLAYLISTS_BY_NAME_REQ, [name, mes.from_user.id]):
        try:
            m = await mes.answer('Плейлист с данным именем уже существует!')
            await asyncio.sleep(3)
            await m.delete()

        except Exception:
            error('Message Deleting:\n' + traceback.format_exc())
            pass

        return

    await state.update_data(playlist_name=name)

    async with state.proxy() as data:
        kb = InlineKeyboard(Call('✅', f'npl:show:{data["page"]}'), Call('❌', f'dpl:page:{data["page"]}'))
        txt = f'<b>Создать плейлист с названием:</b> {name}'

        try:
            await mes.bot.edit_message_text(txt, mes.from_user.id, data['mid'], reply_markup=kb)

        except MessageNotModified:
            pass

        except Exception:
            error('Message Editing:\n' + traceback.format_exc())
            pass

        await StateOn.NewPlaylistAgree.set()


async def create_playlist_kb(playlists: List[PlaylistData], page: int = 1, sl: int = 5, edit_mode: bool = False):
    kb = InlineKeyboardMarkup()

    _slice = playlists[sl * (page - 1):sl * page]
    while not _slice and page > 1:
        page -= 1
        _slice = playlists[sl * (page - 1):sl * page]

    none_btn = IKB(text=' ', callback_data='None')
    create_btn = IKB(text='🔹Создать', callback_data=f'pl:create:{page}')
    change_btn = IKB(text='🔸Изменить', callback_data=f'pl:change:{page}')
    decline_btn = IKB(text='❌Отменить', callback_data=f'pl:page:{page}')

    if _slice:
        m = 'edit' if edit_mode else 'show'
        p = 'switch' if edit_mode else 'page'

        for pl in _slice:
            kb.add(IKB(text=pl.playlist_name, callback_data=f'pl:{m}:{pl.playlist_id}'))

        kb.add(
            IKB(text='◀️', callback_data=f'pl:{p}:{page - 1}') if page - 1 else none_btn,
            IKB(text='🔄', callback_data=f'pl:{p}:{page}'),
            IKB(text='▶️', callback_data=f'pl:{p}:{page + 1}') if len(playlists) > page * sl else none_btn
        )

        kb.add(create_btn, decline_btn if edit_mode else change_btn)

    else:
        kb.add(create_btn)

    return kb


async def add_playlist_kb(playlists: List[PlaylistData], page: int = 1, sl: int = 5, force: bool = False):
    kb = InlineKeyboardMarkup()

    _slice = playlists[sl * (page - 1):sl * page]
    while not _slice and page > 1:
        page -= 1
        _slice = playlists[sl * (page - 1):sl * page]

    none_btn = IKB(text=' ', callback_data='None')
    create_btn = IKB(text='🔹Создать', callback_data=f'pl:create:{page}')
    decline_btn = IKB(text='❌Отменить', callback_data='Close')

    if _slice:
        m = 'show' if not force else 'force'
        p = 'page' if not force else 'fpage'

        for pl in _slice:
            kb.add(IKB(text=pl.playlist_name, callback_data=f'pl:{m}:{pl.playlist_id}'))

        kb.add(
            IKB(text='◀', callback_data=f'pl:{p}:{page - 1}') if page - 1 else none_btn,
            IKB(text='▶', callback_data=f'pl:{p}:{page + 1}') if len(playlists) > page * sl else none_btn
        )

        kb.add(create_btn, decline_btn)

    else:
        kb.add(create_btn)

    return kb


async def add_new_music_input(mes: Message, state: FSMContext, db: SQLite3Database):
    await mes.delete()

    if not mes.audio:
        await error_message(mes, 'Недопустимый тип файла!')
        return

    audio = mes.audio

    async with state.proxy() as data:
        pl_id = int(data["pl_id"])
        db.execute(ADD_NEW_MUSIC_TO_PLAYLIST_REQ, [pl_id, audio.file_id, audio.title, audio.duration])

        playlist = await get_playlist(db, pl_id)

        if not playlist:
            await state.finish()
            return

        tracks = await get_tracks(db, playlist.playlist_id)

        titles = '\n'.join([f'{i}) {t.title}' for i, t in enumerate(tracks, start=1)]) if tracks else 'Нет песен'
        txt = PLAYLIST_TEXT.format(**playlist.get_playlist_txt(titles))

        await send_edit_text(mes, txt, data['mid'], await pl_edit_kb(pl_id))
        await state.finish()


async def rem_music_from_playlist(mes: Message, state: FSMContext, db: SQLite3Database):
    await mes.delete()
    n = mes.text

    if not n.isdigit() or int(n) <= 0:
        await error_message(mes, 'Недопустимый номер песни!')
        return

    async with state.proxy() as data:
        playlist = await get_playlist(db, int(data["pl_id"]))

        if not playlist:
            await state.finish()
            return

        tracks = await get_tracks(db, playlist.playlist_id)

        if int(n) > len(tracks):
            await error_message(mes, 'Недопустимый номер песни!')
            return

        track = tracks[int(n) - 1]
        db.execute(REM_MUSIC_FROM_PLAYLIST_REQ, [track.playlist_id, track.place])

        tracks = await get_tracks(db, playlist.playlist_id)

        titles = '\n'.join([f'{i}) {t.title}' for i, t in enumerate(tracks, start=1)]) if tracks else 'Нет песен'
        txt = PLAYLIST_TEXT.format(**playlist.get_playlist_txt(titles))

        await send_edit_text(mes, txt, data['mid'], await pl_edit_kb(playlist.playlist_id))
        await state.finish()


async def get_playlist(db: SQLite3Database, pl_id: int):
    playlist = db.fetch(GET_PLAYLIST_INFO_BY_PLAYLIST_ID_REQ, [int(pl_id)], one_row=True)
    if not playlist:
        return

    return PlaylistData(*playlist)


async def error_message(mes: Message, txt: str):
    try:
        m = await mes.answer(txt)
        await asyncio.sleep(3)
        await m.delete()

    except Exception:
        error('Message Deleting:\n' + traceback.format_exc())
        pass


async def send_edit_text(mes: Message, txt: str, mid: int, kb: InlineKeyboardMarkup):
    try:
        await mes.bot.edit_message_text(txt, mes.from_user.id, mid, reply_markup=kb)

    except MessageNotModified:
        pass

    except Exception:
        error('Message Editing:\n' + traceback.format_exc())
        pass


async def get_tracks(db: SQLite3Database, pl_id: int):
    return [MusicData(*i) for i in db.fetch(GET_PLAYLIST_MUSIC_BY_PLAYLIST_ID_REQ, [pl_id])]


async def callback_edit_text(call: CallbackQuery, txt: str, kb: InlineKeyboardMarkup):
    try:
        await call.message.edit_text(txt, reply_markup=kb)

    except MessageNotModified:
        pass

    except Exception:
        error('Message Editing:\n' + traceback.format_exc())
        pass
