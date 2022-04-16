from aiogram import Dispatcher
from aiogram.types import ContentType

from resources.tools.cfilters import Command
from resources.tools.states import StateOn
from src.functions import start_func, search_func
from src.functions.main_section.edit_playlist_funcs import editing_playlist_func, rename_playlist_input
from src.functions.main_section.elementary_funcs import choice_video

from aiogram.dispatcher.filters import Text

from src.functions.main_section.playlist_func import playlist_buttons_func, playlist_main_func, \
    new_playlist_name_input_func, add_music_to_playlist, add_new_music_input, rem_music_from_playlist
from src.functions.main_section.settings_func import close_callback


async def register_example_handlers(dp: Dispatcher):
    # You should code handlers in such format
    dp.register_message_handler(
        start_func,
        Command('start'),
        state='*'
    )

    dp.register_message_handler(
        playlist_main_func,
        Text('🎙Мои плейлисты')
    )

    dp.register_message_handler(
        search_func
    )
    dp.register_callback_query_handler(
        choice_video,
        Text(startswith='s:')
    )

    dp.register_callback_query_handler(
        playlist_buttons_func,
        Text(startswith='pl:')
        # State: None -> StateOn.NewPlaylistNameInput (by if)
    )

    dp.register_callback_query_handler(
        playlist_buttons_func,
        Text(startswith='dpl:'),
        state=[StateOn.NewPlaylistNameInput, StateOn.NewPlaylistAgree]
    )

    dp.register_message_handler(
        new_playlist_name_input_func,
        state=StateOn.NewPlaylistNameInput
    )

    dp.register_callback_query_handler(
        playlist_buttons_func,
        Text(startswith='npl:'),
        state=[StateOn.NewPlaylistAgree]
    )

    # добавление песни в плейлист по кнопке, сразу после поиска
    dp.register_callback_query_handler(
        add_music_to_playlist,
        Text('add_to_playlists')
    )

    # Инпут новой песни для плейлиста
    dp.register_message_handler(
        add_new_music_input,
        content_types=ContentType.AUDIO,
        state=StateOn.AddMusicToPlaylistInput
    )

    # Инпут номера песни на удаление
    dp.register_message_handler(
        rem_music_from_playlist,
        state=StateOn.RemMusicFromPlaylistInput
    )

    # Редактировать плейлист
    dp.register_callback_query_handler(
        editing_playlist_func,
        Text(startswith='epl:'),
        state=[
            None, StateOn.RenamePlaylistNameAgree, StateOn.DeletePlaylistAgree
        ]
    )

    # Инпут нового имени для плейлиста
    dp.register_message_handler(
        rename_playlist_input,
        state=StateOn.RenamePlaylistNameInput
    )

    # Close callback func
    dp.register_callback_query_handler(
        close_callback,
        Text('Close')
    )
    # That`s all what you need to know about handlers!
