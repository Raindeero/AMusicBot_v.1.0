ADD_NEW_SEARCH_REQUESTS = '''
INSERT OR IGNORE INTO videos (id, link, title, channel, duration, views, thumbnails, channeid, publishtime, dt)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, strftime('%s','now'))
'''

GET_VIDEO_INFO_BY_ID = '''
SELECT increment, id, link, title, channel, duration, views, thumbnails, channeid, publishtime, dt
FROM videos
WHERE id = ?
'''

GET_VIDEO_INFO_BY_INCREMENT = '''
SELECT increment, id, link, title, channel, duration, views, thumbnails, channeid, publishtime, dt
FROM videos
WHERE increment = ?
'''



GET_PLAYLISTS_OF_USER_REQ = '''
SELECT uid, playlist_id, playlist_name, playlist_caption 
FROM playlists 
WHERE uid = ? ORDER BY playlist_id ASC
'''

GET_PLAYLISTS_BY_NAME_REQ = '''
SELECT * FROM playlists WHERE playlist_name = ? AND uid = ?
'''

CREATE_NEW_PLAYLIST_REQ = '''
INSERT INTO playlists (uid, playlist_name) VALUES (?, ?)
'''

GET_PLAYLIST_INFO_BY_PLAYLIST_ID_REQ = '''
SELECT uid, playlist_id, playlist_name, playlist_caption FROM playlists WHERE playlist_id = ?
'''

GET_NEW_PLAYLIST_INFO_REQ = '''
SELECT uid, playlist_id, playlist_name, playlist_caption FROM playlists WHERE uid = ? and playlist_name = ?
'''

GET_PLAYLIST_MUSIC_BY_PLAYLIST_ID_REQ = '''
SELECT playlist_id, file_id, title, duration, place FROM playlists_content WHERE playlist_id = ? ORDER BY place ASC 
'''

ADD_NEW_MUSIC_TO_PLAYLIST_REQ = '''
INSERT INTO playlists_content (playlist_id, file_id, title, duration) values (?, ?, ?, ?)
'''

RENAME_PLAYLIST_REQ = '''
UPDATE playlists SET playlist_name = ? WHERE playlist_id = ? AND uid = ?
'''

REM_MUSIC_FROM_PLAYLIST_REQ = '''
DELETE FROM playlists_content WHERE playlist_id = ? AND place = ?
'''

DELETE_PLAYLIST_REQ = '''
DELETE FROM playlists WHERE playlist_id = ?
'''

DELETE_PLAYLIST_CONTENT_REQ = '''
DELETE FROM playlists_content WHERE playlist_id = ?
'''
