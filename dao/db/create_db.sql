PRAGMA foreign_keys = ON;
/* 用户表 */
CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name VARCHAR(255) UNIQUE NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    register_date DATETIME NOT NULL DEFAULT (DATETIME('now', 'localtime'))
);
/* 本地音乐表 */
CREATE TABLE music (
    song_id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_name VARCHAR(255) UNIQUE NOT NULL,
    singer_name VARCHAR(255),
    album_name VARCHAR(255),
    song_lan VARCHAR(255),
    song_duration TIME NOT NULL,
    song_path VARCHAR(255) NOT NULL,
    song_cover_path VARCHAR(255),
    song_lyric_path VARCHAR(255)
);
/* 当前播放列表 */
CREATE TABLE cur_playlist (
    play_order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id INTEGER NOT NULL REFERENCES music(song_id) ON UPDATE CASCADE ON DELETE CASCADE
);
/* 音乐播放次数表 */
CREATE TABLE play_count (
    user_id INTEGER NOT NULL REFERENCES user(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
    song_id INTEGER NOT NULL REFERENCES music(song_id) ON UPDATE CASCADE ON DELETE CASCADE,
    song_play_count INTEGER NOT NULL,
    PRIMARY KEY (user_id, song_id)
);
/* 用户收藏列表 */
CREATE TABLE user_like (
    user_id INTEGER NOT NULL REFERENCES user(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
    song_id INTEGER NOT NULL REFERENCES music(song_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (user_id, song_id)
);
/* 用户歌单表 */
CREATE TABLE user_playlist (
    playlist_name VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES user(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
    song_id INTEGER REFERENCES music(song_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (playlist_name, user_id, song_id)
);
/* 创建游客账号 */
INSERT INTO user (user_name, user_password)
VALUES ('guest', '123456');
INSERT INTO user_playlist (playlist_name, user_id)
VALUES (
        '默认歌单',
        (
            SELECT user_id
            FROM user
            WHERE user_name = 'guest'
        )
    );