import sys
import os
curpath = os.path.abspath(os.path.dirname(__file__))
parentpath = os.path.abspath(os.path.dirname(curpath))
sys.path.append(parentpath)
from PyQt5.Qt import QUrl
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from service.app_sql import AppSQL

class MyMusicPlayer(QObject):
    """迷你音乐播放器类。该类封装了音乐播放相关的方法。

    Args:
        QObject (class): 从PyQt5.QtCore继承的QObject类，自定义信号必须继承该类。
    """    

    # 定义类属性
    # 信号必须定义为类属性，否则会报错。
    # 歌曲持续时间更新信号（此时一首新的歌曲开始播放）
    update_song_duration_signal = pyqtSignal(list)  # list: [str: 歌曲名, int: 总毫秒, str: 时分秒]
    # 歌曲播放位置更新信号
    update_song_position_signal = pyqtSignal(list) # list: [str: 歌曲名, int: 总毫秒, str: 时分秒]
    # 歌曲（因删除）终止信号
    song_end_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        """初始化。

        Args:
            parent (QWidgets, optional): QT窗体类。 Defaults to None.
        """        
        super().__init__(parent)
        self.init_global_variable()
        self.init_slot_func()
    
    def init_global_variable(self):
        """设置需要使用的全局变量。
        """
        self.music_player = QMediaPlayer(self)
        self.playlist = QMediaPlaylist(self)
        self.music_player.setPlaylist(self.playlist)  # 设置播放器的播放列表
        self.my_app_sql = AppSQL()
        self.is_init = True
        self.song_name_list = []  # self.playlist中的歌曲
        self.song_lyric_dict = {}  # 歌词文件，以歌曲名：歌词的格式存储。
    
    def init_slot_func(self):
        """设置槽函数。
        """
        self.music_player.durationChanged.connect(self.get_song_duration)
        self.music_player.positionChanged.connect(self.get_song_position)
    
    def _my_emit(self, signal, content):
        """自定义发出信号的函数。

        Args:
            signal (pyqtSignal): 信号名。
            content (Any): 信号内容。
        """        
        signal.emit(content)
    
    def _convert_to_time(self, value):
        """将输入的毫秒总时间转换为以时分秒表示的时间字符串。

        Args:
            value (int): 总时间，毫秒。

        Returns:
            str: 以时分秒格式表示的时间字符串。
        """        
        minutes, seconds = divmod(int(value / 1000), 60)
        hours, minutes = divmod(minutes, 60)
        time_text = "%02d:%02d:%02d" % (hours, minutes, seconds)
        return time_text
    
    def get_song_duration(self, value):
        """歌曲持续时间更新信号的槽函数。

        Args:
            value (int): 总时间，毫秒。
        """        
        time_text = self._convert_to_time(value)
        if self.playlist.currentIndex() == -1:
            self._my_emit(self.song_end_signal, 'Error')
            return  # 这种情况是播放列表中只有一首歌曲，而这首歌曲刚被删除
        song_name = self.song_name_list[self.playlist.currentIndex()]
        self.my_app_sql.change_music_info(
            song_name, 'song_duration', time_text)  # 更新歌曲持续时间信息
        self._my_emit(self.update_song_duration_signal, [song_name, value, time_text])
    
    def get_song_position(self, value):
        """歌曲当前播放位置更新的槽函数。

        Args:
            value (int): 总时间，毫秒。
        """     
        time_text = self._convert_to_time(value)
        if self.playlist.currentIndex() == -1:
            self._my_emit(self.song_end_signal, 'Error')
            return  # 这种情况是播放列表中只有一首歌曲，而这首歌曲刚被删除
        song_name = self.song_name_list[self.playlist.currentIndex()]   
        self._my_emit(self.update_song_position_signal, [song_name, value, time_text])
    
    def _analyze_lyric(self, song_lyric_path):
        """解析lrc歌词文件。

        Args:
            song_lyric_path (str): 歌词文件路径。

        Returns:
            dict: 经过排序的歌词文件。{str: str -> 时间: 歌词}
        """    
        try:    
            with open(song_lyric_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            try:
                with open(song_lyric_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except:
                return
        content_dict = {}
        lyric = {}
        for i in content.splitlines():
            line = i.replace('[', ']').strip().split(']')
            for j in range(len(line) - 1):
                content_dict[line[j].strip()] = line[-1].strip()
        for key in sorted(set(content_dict.keys())):
            try:
                minutes, seconds = key.split(':')
                minutes = int(minutes)
                seconds = float(seconds)
                value = int((minutes * 60 + seconds) * 1000)
                time_text = self._convert_to_time(value)
            except:
                continue  # key不为时间的则跳过
            lyric[time_text] = content_dict[key]
        return lyric
    
    def add_song_to_playlist(self, song_name):
        """将歌曲添加到播放列表。

        Args:
            song_name (str): 歌曲名。
        """        
        ret = self.my_app_sql.search_music(song_name, retrieve_column=['song_path', 'song_lyric_path'],
        is_strict=True)
        if ret:
            song_path = ret[0][0]  # 歌曲路径如果存在则仅有一个
            song_lyric_path = ret[0][1]  # 歌词不一定存在，但如果存在则仅有一个。
        else:
            return
        media_content = QMediaContent(QUrl.fromLocalFile(song_path))
        if not media_content.isNull():
            self.playlist.addMedia(media_content)
            self.song_name_list.append(song_name)
            if song_lyric_path:
                if song_name not in self.song_lyric_dict.keys():
                    lyric = self._analyze_lyric(song_lyric_path)
                    self.song_lyric_dict[song_name] = lyric
            self.my_app_sql.update_cur_playlist(song_name)
            if self.is_init:
                self.is_init = False
                self.playlist.setCurrentIndex(0)
                self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)  # 顺序播放模式
    
    def remove_song_from_playlist(self, song_name):
        """将歌曲从播放列表移除。

        Args:
            song_name (list): 需要移除的歌曲列表。
        """        
        for i in song_name:
            remove_index = [index for (index, value) in enumerate(self.song_name_list) if value == i]
            # 逆序删除
            for j in reversed(remove_index):
                self.song_name_list.pop(j)
                self.playlist.removeMedia(j)
    
    def change_play_order(self):
        """改变歌曲的播放顺序。

        Returns:
            int: 改变后的播放顺序。0: 顺序播放, 1: 随机播放, 2: 列表循环播放 
        """        
        if self.playlist.playbackMode() == QMediaPlaylist.Sequential:
            self.playlist.setPlaybackMode(QMediaPlaylist.Random)  # 顺序播放则切为随机播放
            return 1
        elif self.playlist.playbackMode() == QMediaPlaylist.Random:
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)  # 随机播放则切为列表循环播放
            return 2
        elif self.playlist.playbackMode() == QMediaPlaylist.Loop:
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)  # 列表循环播放则切为顺序播放
            return 0
