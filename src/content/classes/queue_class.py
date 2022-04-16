import io
import sys
from pathlib import Path
from threading import RLock
from typing import Union

from aiogram.types.input_file import _WebPipe, InputFile, CHUNK_SIZE


class QueueCash:
    _lock = RLock()
    in_downloading = {}

    @classmethod
    def update(cls, uid: int, key: str, value, delete: bool = False):
        with cls._lock:
            cls.in_downloading.setdefault(uid, {})[key] = value
            return cls.in_downloading.pop(uid) if delete else cls.in_downloading.get(uid)


class MyWebPipe(_WebPipe):
    def __init__(self, url, uid: int, chunk_size=-1):
        super().__init__(url, chunk_size)
        self.upload_result = 0
        self.uid = uid

    async def __anext__(self):
        if self.closed:
            await self.open()

        chunk = await self.read(self.chunk_size)
        if not chunk:
            QueueCash.update(self.uid, 'upload_size_finish', self.upload_result)
            await self.close()
            raise StopAsyncIteration

        else:
            if self.upload_result:
                self.upload_result += sys.getsizeof(chunk)
            else:
                self.upload_result = sys.getsizeof(chunk)

            QueueCash.update(self.uid, 'upload_size_progress', self.upload_result)

        return chunk


class MyInputFile(InputFile):
    def __init__(self, path_or_bytesio: Union[str, io.IOBase, Path, '_WebPipe'], filename=None, conf=None):
        super().__init__(path_or_bytesio)

    @classmethod
    def from_url(cls, url, filename=None, chunk_size=CHUNK_SIZE, uid: int = None):
        pipe = MyWebPipe(url, uid, chunk_size=chunk_size)
        if filename is None:
            filename = pipe.name

        return cls(pipe, filename)
