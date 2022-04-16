import asyncio
from dataclasses import dataclass

from aiogram.types import CallbackQuery, InputFile
from aiogram.utils.exceptions import BadRequest, MessageNotModified
from aiohttp import ClientSession
from bs4 import BeautifulSoup, element

from resources.models import loop
from resources.models.search_dataclass import YouTubeVideoData
from src.content.classes.queue_class import MyInputFile, QueueCash


@dataclass
class FileData:
    link: str
    type: str
    quality: str
    weight: str


@dataclass
class ResultData:
    audios: list[FileData]


class FileSearcher:
    HOST = 'https://www.yt-download.org/api/button'
    DATA = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/86.0.4240.183 Safari/537.36 OPR/72.0.3815.320'
    }

    SOUP_DATA = {'class': 'download flex flex-wrap sm:inline-flex text-center items-center justify-center'}
    FILEDATA_ZIP = ['link', 'type', 'quality', 'weight']

    @classmethod
    async def _search(cls, result_text: str):
        # Parse by soup
        soup = BeautifulSoup(result_text, 'lxml')

        div_with_downloads = soup.find('div', cls.SOUP_DATA).find_all('a')
        if not div_with_downloads:
            return

        result = []
        for i in div_with_downloads:
            if type(i) is element.NavigableString:
                continue

            d = [i.get('href')]
            for div in i.find_all("div", {"class": "text-shadow-1"}):
                if "text-shadow-1" in div.get('class'):
                    d.append(div.getText().replace('\n', ''))

            result.append(FileData(**dict(zip(cls.FILEDATA_ZIP, d))))

        # Return files
        return result

    @classmethod
    async def main_search(cls, video_id: str):
        # Get request from API
        result = None
        async with ClientSession() as session:
            for i in ('mp3',):
                response_status = 0
                while response_status != 200:
                    async with session.get(f'{cls.HOST}/{i}/{video_id}', data=cls.DATA) as response:
                        print(response.status)
                        if response.status == 200:
                            print('KEK3')
                            result = await response.text()
                            response_status = response.status

                    await asyncio.sleep(1)
        return ResultData(
            audios=await cls._search(result)
        )

    @classmethod
    async def download_file(cls, file: FileData, call: CallbackQuery, video: YouTubeVideoData):
        file_size_max = await cls._get_max_file_max_size(file)
        if file_size_max > 50 * (1024 ** 2):
            await call.answer('Файл весит больше 50 МБ! Невозможно скачать!')
            return

        msg = await call.message.answer('Выполняется скачивание: 0/100%')

        if file.quality.endswith('kbps'):
            # MP3
            func = call.message.answer_audio
            data = {
                'audio': MyInputFile.from_url(file.link, uid=call.from_user.id, file_size_max=file_size_max, msg=msg),
                'title': video.title
            }

        while True:
            try:
                await func(**data)
                break

            except BadRequest:
                await asyncio.sleep(1)

        await msg.edit_text('Выполняется скачивание: 100/100%\nНаслаждайся!')

    @classmethod
    async def _get_max_file_max_size(cls, file: FileData):
        value, b = file.weight.split(' ')
        return int(float(value) * (1024 ** {'B': 0, 'KB': 1, 'MB': 2, 'GB': 3}.get(b)))

