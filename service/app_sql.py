import sys
import os
curpath = os.path.abspath(os.path.dirname(__file__))
parentpath = os.path.abspath(os.path.dirname(curpath))
sys.path.append(parentpath)
from PyQt5.QtCore import QObject, pyqtSignal
from service.common_helper import CommonSQL

class AppSQL(QObject):
    """迷你音乐播放器SQL类。该类封装了前端界面与数据库进行交互的方法。

    Args:
        QObject (class): 从PyQt5.QtCore继承的QObject类，自定义信号必须继承该类。
    """    
        
    # 定义类属性
    # 信号必须定义为类属性，否则会报错。
    # 注册账号或修改密码时的信号
    register_dialog_signal = pyqtSignal(str)  # str: 提示语
    # 账号登录时的信号
    login_dialog_signal = pyqtSignal(str)  # str: 提示语
    # 用户信息更新信号
    update_user_info_signal = pyqtSignal(str)  # str: 当前用户名
    # 创建歌单时的信号
    create_playlist_dialog_signal = pyqtSignal(str)  # str: 提示语
    # 歌单信息更新信号
    update_playlist_signal = pyqtSignal(str) # str: 歌单名

    def __init__(self):
        super().__init__()
    
    def _my_emit(self, signal, content):
        """自定义发出信号的函数。

        Args:
            signal (pyqtSignal): 信号名。
            content (Any): 信号内容。
        """        
        signal.emit(content)
    
    def init_guest(self):
        """初始化游客账号。
        """        
        with CommonSQL() as s:
            s.run_sql('init_guest.sql')
    
    def _check_register_input(self, user_name, password, check_password):
        """检查输入的注册或修改信息是否合法。

        Args:
            user_name (str): 用户名。
            password (str): 密码。
            check_password (str): 密码确认。

        Returns:
            bool: 输入信息是否合法。
        """        
        if  len(user_name) and len(password) and len(check_password):
            if user_name == 'guest':
                self._my_emit(self.register_dialog_signal, '不能对游客账号进行注册或修改！')
            else:
                if password == check_password:
                    return True
                else:
                    self._my_emit(self.register_dialog_signal, '两次输入的密码不一致，请检查！')
        else:
            self._my_emit(self.register_dialog_signal, '存在尚未输入的信息，请检查！')
        return False

    def register_or_change_password(self, user_name, password, check_password,
    chosen_type, table_name='user'):
        """注册账号或修改密码。

        Args:
            user_name (str): 用户名。
            password (str): 密码。
            check_password (str): 密码类型。
            chosen_type (str): 操作类型。register或change_password。
            table_name (str, optional): 指定的表名。 Defaults to 'user'.
        """               
        # 检查输入的注册信息是否合法
        if not self._check_register_input(user_name, password, check_password):
            return
        # 执行注册账号或修改密码操作。
        with CommonSQL() as s:
            check_sql = f"SELECT * FROM {table_name} WHERE user_name = ?"
            ret_num = s.common_sql(user_name, sql=check_sql, is_select=True)
            if chosen_type == 'register':
                if ret_num:
                    self._my_emit(self.register_dialog_signal, '用户已存在，请检查！')
                else:
                    register_sql = f"INSERT INTO {table_name} (user_name, user_password) VALUES (?, ?)"
                    s.common_sql(user_name, password, sql=register_sql)
                    self.create_playlist(user_name, '默认歌单', is_init=True)  # 创建默认歌单
                    self._my_emit(self.register_dialog_signal, '恭喜您，注册成功！')
            elif chosen_type == 'change_password':
                if not ret_num:
                    self._my_emit(self.register_dialog_signal, '用户不存在，请检查！')
                else:
                    field_index = s.sql_query.record().indexOf('user_password')
                    s.sql_query.next()
                    cur_password = s.sql_query.value(field_index)
                    if cur_password == password:
                        self._my_emit(self.register_dialog_signal, '新密码与旧密码不能相同！')
                    else:
                        change_password_sql = \
                        f"UPDATE {table_name} SET user_password = ? WHERE user_name = ?"
                        s.common_sql(password, user_name, sql=change_password_sql)
                        self._my_emit(self.register_dialog_signal, '修改密码成功！')
            
    def _check_login_input(self, user_name, password):
        """检查输入的登录信息是否合法。

        Args:
            user_name (str): 用户名。
            password (str): 密码。

        Returns:
            bool: 输入信息是否合法。
        """        
        if len(user_name) and len(password):
            if user_name == 'guest':
                self._my_emit(self.login_dialog_signal, '不能以游客身份登录！')
            else:
                return True
        else:
            self._my_emit(self.login_dialog_signal, '存在尚未输入的信息，请检查！')
        return False
    
    def login(self, user_name, password, table_name='user'):
        """账号登录。

        Args:
            user_name (str):用户名。
            password (str): 密码。
            table_name (str, optional): 指定的表名。 Defaults to 'user'.
        """        
        # 检查输入的登录信息是否合法
        if not self._check_login_input(user_name, password):
            return
        # 执行登录操作
        with CommonSQL() as s:
            login_sql = f"SELECT * FROM {table_name} WHERE user_name = ? AND user_password = ?"
            ret_num = s.common_sql(user_name, password, sql=login_sql, is_select=True)
            if ret_num:
                self._my_emit(self.login_dialog_signal, '登录成功！')
                self._my_emit(self.update_user_info_signal, user_name)
            else:
                self._my_emit(self.login_dialog_signal, '登录失败，请检查输入！')
    
    def _run_retrieve_sql(self, *args, s: CommonSQL, retrieve_sql, column_num):
        """执行查询语句并取得结果。

        Args:
            s (CommonSQL): 用于执行具体操作的CommonSQL类。
            retrieve_sql (str): 查询SQL语句。
            column_num (int): 查询的字段数。

        Returns:
            list or None: 查询到的每条记录是一个列表，所有记录组成一个总的结果列表。
        """        
        ret_num = s.common_sql(*args, sql=retrieve_sql, is_select=True)
        if ret_num:
            ret = []
            while s.sql_query.next():
                cur_ret = []
                for i in range(column_num):
                    cur_ret.append(str(s.sql_query.value(i)))
                ret.append(cur_ret)
            return ret
    
    def _better_retrieve_ret(self, column_cn, ret):
        """将查询结果以“字段：内容”的形式呈现。

        Args:
            column_cn (list): 字段名。
            ret (list): 查询结果。

        Returns:
            list: 信息表达方式更清晰的查询结果。
        """        
        better_ret = []
        for i in ret:
            cur_better_ret = []
            for j in range(len(i)):
                cur_better_ret.append('：'.join([column_cn[j], i[j]]))
            better_ret.append(cur_better_ret)
        return better_ret

    def get_user_info(self, user_name, table_name='user'):
        """获得当前登录的用户（包括游客）的信息。

        Args:
            user_name (str): 用户名
            table_name (str, optional): 指定的表名。 Defaults to 'user'.

        Returns:
            list or None: 用户信息。
        """        
        with CommonSQL() as s:
            retrieve_column = ['user_id', 'user_name', 'register_date']
            retrieve_column_cn = ['用户编号', '用户名', '注册时间']
            retrieve_sql = f"SELECT {', '.join(retrieve_column)} FROM {table_name} WHERE user_name = ?"
            ret = self._run_retrieve_sql(user_name, s=s, retrieve_sql=retrieve_sql,
            column_num=len(retrieve_column))
            return self._better_retrieve_ret(retrieve_column_cn, ret)
    
    def search_music(self, search_text, table_name='music', retrieve_column=['song_id'], is_strict=False):
        """搜索音乐。

        Args:
            search_text (str): 搜索信息。
            table_name (str, optional): 指定的表名。 Defaults to 'music'.
            column_name(list, optional): 指定要获取的字段列表，仅用于严格模式。 Defaults to ['song_id'].
            is_strict (bool): 严格模式。用于精确搜索指定歌曲名的歌曲信息。 Defaults to False.

        Returns:
            list or str: 搜索结果或输入不合法提示语。
        """        
        # 检查输入的搜索信息是否合法
        if not search_text:
            return '请输入搜索内容！'
        # 执行严格模式下的搜索操作
        if is_strict:
            with CommonSQL() as s:
                retrieve_sql = f"SELECT {', '.join(retrieve_column)} FROM {table_name} WHERE song_name = ?"
                ret = self._run_retrieve_sql(search_text, s=s, retrieve_sql=retrieve_sql,
                column_num=len(retrieve_column))
                return ret
        # 执行搜索操作
        with CommonSQL() as s:
            search_text = ''.join(['%', search_text, '%'])
            retrieve_column = ['song_name', 'singer_name',
            'album_name', 'song_lan', 'song_duration']
            # retrieve_column_cn = ['歌曲名', '演唱者', '专辑名', '语言', '歌曲时长']
            retrieve_sql = f"SELECT {', '.join(retrieve_column)} FROM {table_name} \
                WHERE song_name LIKE ? OR singer_name LIKE ? OR album_name LIKE ?"
            ret = self._run_retrieve_sql(search_text, search_text, search_text,
            s=s, retrieve_sql=retrieve_sql, column_num=len(retrieve_column))
            ret = [] if not ret else ret
            return ret
    
    def get_user_play_count(self, user_name, table_name=['user', 'music', 'play_count']):
        """获得当前登录的用户的播放排行表。

        Args:
            user_name (str): 用户名。
            table_name (list, optional): 指定的表名。 Defaults to ['user', 'music', 'play_count'].

        Returns:
            list or None: 歌曲和播放次数信息。
        """        
        with CommonSQL() as s:
            retrieve_column = ['play_count.song_play_count', 'music.song_name',
            'music.singer_name', 'music.album_name', 'music.song_lan', 'music.song_duration']
            # retrieve_column_cn = ['播放次数', '歌曲名', '演唱者', '专辑名', '语言', '歌曲时长']
            retrieve_sql = f"SELECT {', '.join(retrieve_column)} FROM {', '.join(table_name)} \
                WHERE user.user_name = ? AND play_count.user_id = user.user_id \
                    AND play_count.song_id = music.song_id ORDER BY play_count.song_play_count DESC"
            ret = self._run_retrieve_sql(user_name, s=s, retrieve_sql=retrieve_sql,
            column_num=len(retrieve_column))
            return ret
    
    def update_user_play_count(self, user_name, song_name, table_name=['user', 'music', 'play_count']):
        """更新当前登录的用户的播放排行表。

        Args:
            user_name (str): 用户名。
            song_name (str): 歌曲名。
            table_name (list, optional): 指定的表名。 Defaults to ['user', 'music', 'play_count'].
        """        
        with CommonSQL() as s:
            query_sql = f"SELECT * FROM {table_name[-1]} \
                WHERE play_count.user_id = (SELECT user_id FROM {table_name[0]} WHERE user_name = ?) \
                    AND play_count.song_id = (SELECT song_id FROM {table_name[1]} WHERE song_name = ?)"
            ret = s.common_sql(user_name, song_name, sql=query_sql, is_select=True)
            if ret:
                update_sql = f"UPDATE {table_name[-1]} SET song_play_count = song_play_count + 1 WHERE \
                    play_count.user_id = (SELECT user_id FROM {table_name[0]} WHERE user_name = ?) AND \
                        play_count.song_id = (SELECT song_id FROM {table_name[1]} WHERE song_name = ?)"
            else:
                update_sql = f"INSERT INTO {table_name[-1]} (user_id, song_id, song_play_count) VALUES \
                    ((SELECT user_id FROM {table_name[0]} WHERE user_name = ?), \
                    (SELECT song_id FROM {table_name[1]} WHERE song_name = ?), 1)"
            s.common_sql(user_name, song_name, sql=update_sql)
    
    def get_user_like(self, user_name, table_name=['user, music, user_like']):
        """获得当前登录的用户的收藏列表。

        Args:
            user_name (str): 用户名。
            table_name (list, optional): 指定的表名。 Defaults to ['user, music, user_like'].

        Returns:
            list or None: 歌曲信息。
        """        
        with CommonSQL() as s:
            retrieve_column = ['music.song_name', 'music.singer_name',
            'music.album_name', 'music.song_lan', 'music.song_duration']
            # retrieve_column_cn = ['歌曲名', '演唱者', '专辑名', '语言', '歌曲时长']
            retrieve_sql = f"SELECT {', '.join(retrieve_column)} FROM {', '.join(table_name)} \
                WHERE user.user_name = ? AND user_like.user_id =user.user_id \
                    AND user_like.song_id = music.song_id"
            ret = self._run_retrieve_sql(user_name, s=s, retrieve_sql=retrieve_sql,
            column_num=len(retrieve_column))
            return ret
    
    def add_to_playlist(self, user_name, playlist_name, song_name, table_name=['user', 'music', 'user_playlist']):
        """将指定歌曲添加到指定歌单。

        Args:
            user_name (str)): 用户名。
            playlist_name (str): 歌单名。
            song_name (list): 歌曲名列表，可能有一个或多个元素。
            table_name (list, optional): 指定的表名。 Defaults to ['user', 'music', 'user_playlist'].
        """        
        with CommonSQL() as s:
            for i in song_name:
                add_sql = f"INSERT INTO {table_name[-1]} VALUES \
                    (?, (SELECT user_id FROM {table_name[0]} WHERE user_name = ?), \
                    (SELECT song_id FROM {table_name[1]} WHERE song_name = ?))"
                try:
                    s.common_sql(playlist_name, user_name, i, sql=add_sql)  # 重复添加不会成功，但可能引发异常。
                except:
                    pass
    
    def add_user_like_song(self, user_name, song_name, table_name = ['user', 'music', 'user_like']):
        """将歌曲加入到用户收藏列表。

        Args:
            user_name (str): 用户名。
            song_name (str): 歌曲名。
            table_name (list, optional): 指定的表名。 Defaults to ['user', 'music', 'user_like'].
        """        
        with CommonSQL() as s:
            add_sql = f"INSERT INTO {table_name[-1]} (user_id, song_id) VALUES \
                ((SELECT user_id FROM {table_name[0]} WHERE user_name = ?), \
                    (SELECT song_id FROM {table_name[1]} WHERE song_name = ?))"
            s.common_sql(user_name, song_name, sql=add_sql)

    def del_user_like_song(self, user_name, song_name, table_name = ['user', 'music', 'user_like']):
        """删除用户收藏列表中的指定歌曲。

        Args:
            user_name (str): 用户名。
            song_name (list): 歌曲名列表，可能有一个或多个元素。
            table_name (list, optional): 指定的表名。 Defaults to ['user', 'music', 'user_like'].
        """        
        with CommonSQL() as s:            
            for i in song_name:
                del_sql = f"DELETE FROM {table_name[-1]} WHERE \
                    user_id = (SELECT user_id FROM {table_name[0]} WHERE user_name = ?) AND \
                        song_id = (SELECT song_id FROM {table_name[1]} WHERE song_name = ?)"
                s.common_sql(user_name, i, sql=del_sql)
    
    def _check_playlist_input(self, playlist_name):
        """检查输入的歌单信息是否合法。

        Args:
            playlist_name (str): 歌单名。

        Returns:
            bool: 输入信息是否合法。
        """        
        if len(playlist_name):
            if playlist_name == '默认歌单':
                self._my_emit(self.create_playlist_dialog_signal, '不能以默认歌单作为歌单名！')
            else:
                return True
        else:
            self._my_emit(self.create_playlist_dialog_signal, '存在尚未输入的信息，请检查！')
        return False
    
    def create_playlist(self, user_name, playlist_name, table_name=['user', 'user_playlist'], is_init=False):
        """为指定用户创建歌单。

        Args:
            user_name (str): 用户名。
            playlist_name (str): 歌单名。
            table_name (list, optional): 指定的表名。 Defaults to ['user', 'user_playlist'].
            is_init (bool, optional): 是否为初始化，若是初始化则不作输入信息检查。 Defaults to False.
        """              
        # 检查输入的歌单信息是否合法
        if not is_init:
            if not self._check_playlist_input(playlist_name):
                return
        # 执行创建歌单操作
        with CommonSQL() as s:
            check_sql = f"SELECT * FROM {', '.join(table_name)} WHERE user.user_name = ? \
                AND user_playlist.playlist_name = ? AND user_playlist.user_id = user.user_id"
            ret = s.common_sql(user_name, playlist_name, sql=check_sql, is_select=True)
            if ret:
                self._my_emit(self.create_playlist_dialog_signal, '歌单已存在，请检查！')
            else:
                create_sql = f"INSERT INTO {table_name[-1]} (user_id, playlist_name) VALUES \
                    ((SELECT user_id FROM {table_name[0]} WHERE user_name = ?), ?)"
                s.common_sql(user_name, playlist_name, sql=create_sql)
                self._my_emit(self.create_playlist_dialog_signal, '歌单创建成功！')
                self._my_emit(self.update_playlist_signal, playlist_name)
    
    def del_playlist(self, user_name, playlist_name, table_name=['user', 'user_playlist']):
        """删除指定用户的指定歌单。

        Args:
            user_name (str): 用户名。
            playlist_name (str): 歌单名。
            table_name (list, optional): 指定的表名。 Defaults to ['user', 'user_playlist'].
        """        
        with CommonSQL() as s:
            del_sql = f"DELETE FROM {table_name[-1]} WHERE user_playlist.user_id = \
                (SELECT user_id FROM {table_name[0]} WHERE user_name = ?) AND \
                    playlist_name = ?"
            s.common_sql(user_name, playlist_name, sql=del_sql)
    
    def get_user_playlist_name(self, user_name, table_name=['user', 'user_playlist']):
        """获取当前登录的用户创建的歌单名（不包括默认歌单）。

        Args:
            user_name (str): 用户名。
            table_name (list, optional): 指定的表名。 Defaults to ['user', 'user_playlist'].

        Returns:
            list or None: 歌单名。
        """        
        with CommonSQL() as s:
            retrieve_column = 'playlist_name'
            # retrieve_column_cn = '歌单名'
            retrieve_sql = f"SELECT DISTINCT {retrieve_column} FROM {', '.join(table_name)} \
                WHERE user.user_name = ? AND user_playlist.user_id = user.user_id \
                    AND {retrieve_column} IS NOT '默认歌单'"
            ret = self._run_retrieve_sql(user_name, s=s, retrieve_sql=retrieve_sql, column_num=1)
            return ret
    
    def get_user_playlist(self, user_name, playlist_name, table_name=['user', 'music', 'user_playlist']):
        """获得当前登录的用户的指定歌单。

        Args:
            user_name (str): 用户名。
            playlist_name (str): 指定的歌单名。
            table_name (list, optional): 指定的表名。 Defaults to ['user', 'music', 'user_playlist'].

        Returns:
            list or None: 歌曲信息。
        """        
        with CommonSQL() as s:            
            retrieve_column = ['music.song_name', 'music.singer_name',
            'music.album_name', 'music.song_lan', 'music.song_duration']
            # retrieve_column_cn = ['歌曲名', '演唱者', '专辑名', '语言', '歌曲时长']
            retrieve_sql = f"SELECT {', '.join(retrieve_column)} FROM {', '.join(table_name)} \
                WHERE user.user_name = ? AND user_playlist.playlist_name = ? \
                    AND user_playlist.user_id = user.user_id AND user_playlist.song_id = music.song_id"
            ret = self._run_retrieve_sql(user_name, playlist_name, s=s, retrieve_sql=retrieve_sql,
            column_num=len(retrieve_column))
            return ret
    
    def get_local_music(self, table_name='music'):
        """获取所有本地音乐。

        Args:
            table_name (str, optional): 指定的表名。 Defaults to 'music'.

        Returns:
            list or None: 歌曲信息。
        """        
        with CommonSQL() as s:
            retrieve_column = ['song_name', 'singer_name',
            'album_name', 'song_lan', 'song_duration']
            # retrieve_column_cn = ['歌曲名', '演唱者', '专辑名', '语言', '歌曲时长']
            retrieve_sql = f"SELECT {', '.join(retrieve_column)} FROM {table_name}"
            ret = self._run_retrieve_sql(s=s, retrieve_sql=retrieve_sql, column_num=len(retrieve_column))
            return ret
    
    def change_music_info(self, song_name, changed_column_name, changed_text, table_name='music'):
        """修改指定歌曲的信息。

        Args:
            song_name (str): 歌曲名。
            changed_column_name (str): 要修改的字段。
            changed_text (str): 修改后的内容。
            table_name (str, optional): 指定的表名。 Defaults to 'music'.
        """        
        with CommonSQL() as s:
            update_sql = f"UPDATE {table_name} SET {changed_column_name} = ? WHERE song_name = ?"
            s.common_sql(changed_text, song_name, sql=update_sql)
    
    def add_local_music(self, song_name, song_path, song_duration='00:00:00', table_name='music'):
        """添加歌曲。

        Args:
            song_name (str): 歌曲名。
            song_path (str): 歌曲的本地路径。
            song_duration (str, optional): 歌曲的时长。 Defaults to '00:00:00'.
            table_name (str, optional): 指定的表名。 Defaults to 'music'.
        """        
        with CommonSQL() as s:
            add_sql = f"INSERT INTO {table_name} (song_name, song_duration, song_path) VALUES \
                (?, ?, ?)"
            s.common_sql(song_name, song_duration, song_path, sql=add_sql)
    
    def del_local_music(self, song_name, table_name='music'):
        """删除歌曲。

        Args:
            song_name (str): 歌曲名。
            table_name (str, optional): 指定的表名。 Defaults to 'music'.
        """    
        with CommonSQL() as s:
            foreign_keys_sql = "PRAGMA foreign_keys = ON"  # 此句是为了外键约束生效，以保证级联删除能起作用。
            s.common_sql(sql=foreign_keys_sql)
            del_sql = f"DELETE FROM {table_name} WHERE song_name = ?"
            s.common_sql(song_name, sql=del_sql)   
    
    def update_cur_playlist(self, song_name, table_name=['cur_playlist', 'music']):
        """更新当前播放列表。

        Args:
            song_name (str): 歌曲名。
            table_name (list, optional): 指定的表名。 Defaults to ['cur_playlist', 'music'].
        """        
        with CommonSQL() as s:
            update_sql = f"INSERT INTO {table_name[0]} (song_id) VALUES \
                ((SELECT song_id FROM {table_name[-1]} WHERE song_name = ?))"
            s.common_sql(song_name, sql=update_sql)
    
    def get_cur_playlist(self, table_name=['cur_playlist', 'music']):
        """获取当前播放列表中的音乐信息。

        Args:
            table_name (str, optional): 指定的表名。 Defaults to ['cur_playlist', 'music'].

        Returns:
            list or None: 歌曲信息。
        """        
        with CommonSQL() as s:
            retrieve_column = ['music.song_name', 'music.singer_name',
            'music.album_name', 'music.song_lan', 'music.song_duration']
            # retrieve_column_cn = ['歌曲名', '演唱者', '专辑名', '语言', '歌曲时长']
            retrieve_sql = f"SELECT {', '.join(retrieve_column)} FROM {', '.join(table_name)} \
                WHERE cur_playlist.song_id = music.song_id \
                    ORDER BY cur_playlist.play_order_id"
            ret = self._run_retrieve_sql(s=s, retrieve_sql=retrieve_sql, column_num=len(retrieve_column))
            return ret
