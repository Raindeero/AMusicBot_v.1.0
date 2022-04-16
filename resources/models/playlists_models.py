from dataclasses import dataclass


@dataclass
class PlaylistData:
    uid: int
    playlist_id: int
    playlist_name: str
    playlist_caption: str

    def get_playlist_txt(self, titles):
        return {
            'playlist_name': self.playlist_name,
            'playlist_titles': titles
        }

@dataclass
class MusicData:
    playlist_id: int
    file_id: str
    title: str
    duration: int
    place: int