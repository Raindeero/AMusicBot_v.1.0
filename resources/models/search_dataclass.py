import json
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SearchResult:
    index: int
    id: str
    link: str
    title: str
    channel: str
    duration: str
    views: int
    thumbnails: list
    channeId: str
    publishTime: str

    @property
    def json_thumbnails(self):
        return json.dumps({i: v for i, v in enumerate(self.thumbnails)})

    def get_for_insert(self):
        return self.id, self.link, self.title, self.channel, self.duration, self.views, self.json_thumbnails, \
               self.channeId, self.publishTime

@dataclass
class YouTubeVideoData:
    increment: int
    id: str
    link: str
    title: str
    channel: str
    duration: str
    views: int
    thumbnails: list
    channeid: str
    publishtime: str
    dt: datetime
