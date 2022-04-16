from json import loads

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.types import Message, CallbackQuery, InputFile
from pytube import YouTube, Stream

from resources.models.search_dataclass import SearchResult, YouTubeVideoData
from resources.tools.database import SQLite3Database
from resources.tools.keyboards import InlineKeyboard, Call, ReplyKeyboard

from youtubesearchpython import SearchVideos

from src.content.classes.queue_class import QueueCash
from src.content.consts.db_requests import ADD_NEW_SEARCH_REQUESTS, GET_VIDEO_INFO_BY_ID


async def start_func(mes: Message, state: FSMContext):
    kb = ReplyKeyboard('🎙Мои плейлисты')
    await mes.answer("Отправь мне название или ссылку на видео в ютубе и я тебе верну аудио", reply_markup=kb)
    await state.finish()


async def search_func(mes: Message, db: SQLite3Database):
    try:
        await mes.delete()
    except Exception:
        pass
    kb = InlineKeyboard(Call('Добавить в плейлист', 'add_playlist'))

    search_results = SearchVideos(mes.text, max_results=5, language='ru-RU', region='RU').result()
    if not search_results:
        await mes.answer('Никаких совпадений по запросу.')
        return

    kb_list, db_list = [], []
    for res in loads(search_results).get('search_result'):
        r = SearchResult(**res)

        kb_list.append(Call(r.duration + ' ' + r.title, f's:{r.id}'))
        db_list.append(r.get_for_insert())
    db.execute(ADD_NEW_SEARCH_REQUESTS, db_list, many=True)

    answer = f'<b>Результаты по запросу</b>: {mes.text}'
    keyboard = InlineKeyboard(*kb_list, row_width=1)

    await mes.answer(answer, reply_markup=keyboard, disable_web_page_preview=False)


async def choice_video(call: CallbackQuery, db: SQLite3Database):
    await call.answer('Ищу информацию по видео...')
    result = db.fetch(GET_VIDEO_INFO_BY_ID, [call.data.replace('s:', '')], one_row=True)
    if not result:
        await call.answer('Произошла ошибка! Данного видео не существует, повторите поиск!')
        return

    if call.from_user.id in QueueCash.in_downloading:
        await call.answer('Вы уже скачиваете файл! Подождите!')
        return

    result = YouTubeVideoData(*result)
    yt = YouTube(result.link)
    audio: Stream = yt.streams.filter(type='audio').last()
    if audio.filesize > 52428800:
        audio: Stream = yt.streams.filter(type='audio').first()
        if audio.filesize > 52428800:
            await call.answer('Размер аудио слишком большой, невозможно отправить')

    kb = InlineKeyboard(Call('Добавить в мои плейлисты', 'add_to_playlists'))

    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer_audio(InputFile(audio.download('download_cash')), title=audio.title,
                                    performer=result.channel, reply_markup=kb)
