from aiogram.dispatcher.filters.state import StatesGroup, State


class StateOn(StatesGroup):
    # Create playlist
    NewPlaylistNameInput = State()
    NewPlaylistAgree = State()

    # Change playlist name
    RenamePlaylistNameInput = State()
    RenamePlaylistNameAgree = State()

    # Add new music to playlist
    AddMusicToPlaylistInput = State()

    # Remove music from playlist
    RemMusicFromPlaylistInput = State()

    # Swap music in playlist
    SwapMusicInPlaylistInput1st = State()
    SwapMusicInPlaylistInput2nd = State()

    # Delete playlist
    DeletePlaylistAgree = State()
