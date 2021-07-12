/* 初始化游客账号 */
DELETE FROM play_count
WHERE play_count.user_id = (
        SELECT user_id
        FROM user
        WHERE user_name = 'guest'
    );
DELETE FROM user_like
WHERE user_like.user_id = (
        SELECT user_id
        FROM user
        WHERE user_name = 'guest'
    );
DELETE FROM user_playlist
WHERE user_playlist.user_id = (
        SELECT user_id
        FROM user
        WHERE user_name = 'guest'
    );
UPDATE user
SET register_date = (DATETIME('now', 'localtime'))
WHERE user_name = 'guest';
/* 初始化现有的播放列表 */
DELETE FROM cur_playlist;