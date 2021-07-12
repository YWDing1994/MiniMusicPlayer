import sys
import os
curpath = os.path.abspath(os.path.dirname(__file__))
parentpath = os.path.abspath(os.path.dirname(curpath))
sys.path.append(parentpath)
from random import sample
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QTableWidgetItem, QListWidgetItem, QFileDialog
from PyQt5.QtGui import QCursor
from ui.Ui_main_window import Ui_MainWindow
from ui.call_login_dialog import MyLoginDialog
from ui.call_message_box import MyMessageBox
from ui.call_create_playlist_dialog import MyCreatePlaylistDialog
from ui.common_helper import CommmonHelper, SetQTableWidgetEditable
from service.app_sql import AppSQL
from service.music_player import MyMusicPlayer

class MyMainWindow(QMainWindow, Ui_MainWindow):
    """根据UI设计和业务逻辑设置主界面。

    Args:
        QMainWindow (class): 从PyQt5.QtWidgets引入的QMainWindow类。
        Ui_MainWindow (class): 主界面的UI设计类。
    """    

    def __init__(self, parent=None):        
        super().__init__(parent)
        self.setupUi(self)
        self.init_main_window()
        qss_filename = 'default_ui_main_window.qss'
        qss_style = CommmonHelper.load_qss(qss_filename)
        if qss_style:
            self.setStyleSheet(qss_style)  # 加载QSS样式表以设置界面风格
        self.init_global_variable()
        self.show_music(is_init=True)
        self.init_slot_func()

    def init_main_window(self):
        """设置主界面的某些显示效果。
        """        
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置主界面无边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置主界面背景透明
        self.setAttribute(Qt.WA_NoSystemBackground, False)  # 使主界面背景透明不影响border-image绘制
        self.playHorizontalSlider.setEnabled(False)  # 未开始播放音乐时先禁止滑动条
        self.init_table_widget()  # 设置表格控件
    
    def init_table_widget(self):
        """设置表格控件的某些显示效果。
        """
        # 设置水平方向表格为自适应的伸缩模式
        self.curPlayTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.songRankedTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.userLikeTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.playlistSongTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.localMusicTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.searchRetTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格的不可编辑列
        song_ranked_uneditable = [0, 1, 5]  # 播放次数，歌曲名，时长
        SetQTableWidgetEditable.set_column(self.songRankedTableWidget, song_ranked_uneditable)
        other_uneditable = [0, 4]  # 歌曲名，时长
        SetQTableWidgetEditable.set_column(self.curPlayTableWidget, other_uneditable)
        SetQTableWidgetEditable.set_column(self.userLikeTableWidget, other_uneditable)
        SetQTableWidgetEditable.set_column(self.playlistSongTableWidget, other_uneditable)
        SetQTableWidgetEditable.set_column(self.localMusicTableWidget, other_uneditable)
        SetQTableWidgetEditable.set_column(self.searchRetTableWidget, other_uneditable)
    
    # 使主界面在无边框的情况下可以拖曳移动
    def mousePressEvent(self, event):        
        if event.button() == Qt.LeftButton:
            self.move_drag = True
            self.move_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
    
    def mouseMoveEvent(self, QMouseEvent):
        try:  # 拖动时偶尔会引发不存在move_drag属性的异常
            if Qt.LeftButton and self.move_drag:
                self.move(QMouseEvent.globalPos() - self.move_drag_pos)
                QMouseEvent.accept()
        except:
            pass
    
    def mouseReleaseEvent(self, QMouseEvent):
        self.move_drag = False
        self.setCursor(QCursor(Qt.ArrowCursor))
    
    def init_global_variable(self):
        """设置需要使用的全局变量。
        """
        self.max_size = [self.maximumWidth(), self.maximumHeight()]  # 主界面的最大尺寸
        self.pre_size = [self.width(), self.height()]  # 主界面变化前的尺寸
        self.my_app_sql = AppSQL()
        self.my_app_sql.init_guest()
        self.cur_user = 'guest'  # 当前登录的用户
        self.userInfoListWidget.addItems(*self.my_app_sql.get_user_info(self.cur_user))  # 显示游客信息
        self.is_login = False  # 登录状态，默认为未登录。
        self.my_music_player = MyMusicPlayer(self)
    
    def show_music(self, is_init=False):
        """显示本地音乐和首页推荐音乐。

        Args:
            is_init (bool, optional): 是否是初始化，若是则显示每日音乐推荐。 Defaults to False.
        """        
        ret = self.my_app_sql.get_local_music()
        self._update_table_widget(self.localMusicTableWidget, ret)
        if is_init:
            set_visible = lambda l, is_visible: [i.setVisible(is_visible) for i in l]
            set_visible([self.recSongBtn_1, self.recSongBtn_2, self.recSongBtn_3,
            self.recSongBtn_4, self.recSongBtn_5, self.recSongNameLbl_1, self.recSongNameLbl_2,
            self.recSongNameLbl_3, self.recSongNameLbl_4, self.recSongNameLbl_5], False)
            if not ret:
                return
            cnt = len(ret)  # 本地音乐总数
            btn = [self.recSongBtn_1, self.recSongBtn_2, self.recSongBtn_3,
            self.recSongBtn_4, self.recSongBtn_5]
            lbl = [self.recSongNameLbl_1, self.recSongNameLbl_2, self.recSongNameLbl_3,
            self.recSongNameLbl_4, self.recSongNameLbl_5]
            if cnt < 5:
                song_name_list = [ret[i][0] for i in range(cnt)]
                rec_num = cnt
            else:
                index = sample([i for i in range(cnt)], 5)
                song_name_list = [ret[i][0] for i in index]
                rec_num = 5
            for i in range(rec_num):
                set_visible([btn[i], lbl[i]], True)
                song_name = song_name_list[i]
                song_cover_path = self.my_app_sql.search_music(song_name, retrieve_column=['song_cover_path'],
                is_strict=True)[0][0]  # 若不存在歌词则返回[[]]
                lbl[i].setText(song_name)
                if song_cover_path:
                    song_cover_path = '\"' +song_cover_path + '\"'
                    qss_style = '''
                    QPushButton
                    {
                        border-image: url(%s);
                    }
                    QPushButton:hover
                    {
                        border-image: url("./ui/resource/icon/recsong_hover.svg");
                    }
                    QPushButton:pressed
                    {
                        border-image: url("./ui/resource/icon/recsong_pressed.svg");
                    }
                    ''' % (song_cover_path)
                    btn[i].setStyleSheet(qss_style)

    def init_slot_func(self):
        """设置主界面各控件的槽函数。
        """       
        # 按钮 
        # 关闭，最小化，最大化按钮
        self.closeBtn.clicked.connect(self.slot_closeBtn_clicked)
        self.minBtn.clicked.connect(self.showMinimized)
        self.maxBtn.clicked.connect(self.slot_maxBtn_clicked)
        # 用户登录按钮
        self.userLoginBtn.clicked.connect(self.slot_userLoginBtn_clicked)
        # 子界面切换：我的信息，我的收藏，我的歌单，本地音乐按钮
        self.userInfoBtn.clicked.connect(lambda: self.slot_changeStackedWidgetBtn_clicked(1))
        self.userLikelistBtn.clicked.connect(lambda: self.slot_changeStackedWidgetBtn_clicked(2))
        self.userPlaylistBtn.clicked.connect(lambda: self.slot_changeStackedWidgetBtn_clicked(3))
        self.localMusicBtn.clicked.connect(lambda: self.slot_changeStackedWidgetBtn_clicked(4))
        # 改变歌曲播放顺序，上一首，播放，下一首，收藏按钮
        self.playOrderBtn.clicked.connect(self.slot_playOrderBtn_clicked)
        self.preSongBtn.clicked.connect(self.slot_preSongBtn_clicked)
        self.playBtn.clicked.connect(self.slot_playBtn_clicked)
        self.nextSongBtn.clicked.connect(self.slot_nextSongBtn_clicked)
        self.likeBtn.clicked.connect(self.slot_likeBtn_clicked)
        # 搜索按钮
        self.searchBtn.clicked.connect(self.slot_searchBtn_clicked)
        # 推荐音乐按钮
        self.recSongBtn_1.clicked.connect(lambda:
        self.slot_recSongBtn_clicked(self.recSongBtn_1, self.recSongNameLbl_1))
        self.recSongBtn_2.clicked.connect(lambda:
        self.slot_recSongBtn_clicked(self.recSongBtn_2, self.recSongNameLbl_2))
        self.recSongBtn_3.clicked.connect(lambda:
        self.slot_recSongBtn_clicked(self.recSongBtn_3, self.recSongNameLbl_3))
        self.recSongBtn_4.clicked.connect(lambda:
        self.slot_recSongBtn_clicked(self.recSongBtn_4, self.recSongNameLbl_4))
        self.recSongBtn_5.clicked.connect(lambda:
        self.slot_recSongBtn_clicked(self.recSongBtn_5, self.recSongNameLbl_5))
        # 添加到歌单按钮
        self.addToPlaylistBtn.clicked.connect(self.slot_addToPlaylistBtn_clicked)
        # 从收藏中移除按钮
        self.delLikeSongBtn.clicked.connect(self.slot_delLikeSongBtn_clicked)
        # 创建歌单按钮
        self.createPlaylistBtn.clicked.connect(self.slot_createPlaylistBtn_clicked)
        # 删除歌单按钮
        self.delPlaylistBtn.clicked.connect(self.slot_delPlaylistBtn_clicked)
        # 添加歌曲按钮
        self.addSongBtn.clicked.connect(self.slot_addSongBtn_clicked)
        # 删除歌曲按钮
        self.delSongBtn.clicked.connect(self.slot_delSongBtn_clicked)
        # 列表控件的信号
        # 切换歌单
        self.userPlaylistWidget.itemClicked.connect(self.slot_user_playlist_item_clicked)
        # 表格控件的信号
        # 修改歌曲信息
        self.curPlayTableWidget.cellClicked.connect(lambda row, column:
        self.slot_table_widget_cell_clicked(row, column, table_widget=self.curPlayTableWidget))
        self.songRankedTableWidget.cellClicked.connect(lambda row, column:
        self.slot_table_widget_cell_clicked(row, column, table_widget=self.songRankedTableWidget,
        start=1))
        self.userLikeTableWidget.cellClicked.connect(lambda row, column:
        self.slot_table_widget_cell_clicked(row, column, table_widget=self.userLikeTableWidget))
        self.playlistSongTableWidget.cellClicked.connect(lambda row, column:
        self.slot_table_widget_cell_clicked(row, column, table_widget=self.playlistSongTableWidget))
        self.localMusicTableWidget.cellClicked.connect(lambda row, column:
        self.slot_table_widget_cell_clicked(row, column, table_widget=self.localMusicTableWidget))
        self.searchRetTableWidget.cellClicked.connect(lambda row, column:
        self.slot_table_widget_cell_clicked(row, column, table_widget=self.searchRetTableWidget))
        # 音乐播放信号
        self.my_music_player.update_song_duration_signal.connect(self.slot_update_song_duration_signal)
        self.my_music_player.update_song_position_signal.connect(self.slot_update_song_position_signal)
        self.my_music_player.song_end_signal.connect(self.slot_song_end_signal)
        self.playHorizontalSlider.sliderMoved.connect(self.slot_sliderMoved)
        self.curPlayTableWidget.cellDoubleClicked.connect(lambda row, column:
        self.slot_table_widget_cell_doubleclicked(row, column, table_widget=self.curPlayTableWidget))
        self.songRankedTableWidget.cellDoubleClicked.connect(lambda row, column:
        self.slot_table_widget_cell_doubleclicked(row, column, table_widget=self.songRankedTableWidget,
        start=1))
        self.userLikeTableWidget.cellDoubleClicked.connect(lambda row, column:
        self.slot_table_widget_cell_doubleclicked(row, column, table_widget=self.userLikeTableWidget))
        self.playlistSongTableWidget.cellDoubleClicked.connect(lambda row, column:
        self.slot_table_widget_cell_doubleclicked(row, column, table_widget=self.playlistSongTableWidget))
        self.localMusicTableWidget.cellDoubleClicked.connect(lambda row, column:
        self.slot_table_widget_cell_doubleclicked(row, column, table_widget=self.localMusicTableWidget))
        self.searchRetTableWidget.cellDoubleClicked.connect(lambda row, column:
        self.slot_table_widget_cell_doubleclicked(row, column, table_widget=self.searchRetTableWidget))

    def slot_closeBtn_clicked(self):
        """关闭按钮单击时的槽函数。
        """
        check_msgbox = MyMessageBox(self, '您确定要退出迷你音乐播放器吗？', btn_num=2)
        if check_msgbox.check_clicked:
            self.close()
        
    def slot_maxBtn_clicked(self):
        """最大化按钮单击时的槽函数。
        """ 
        width, height = self.width(), self.height()
        if width < self.max_size[0] or height < self.max_size[1]:
            self.resize(*self.max_size)
            self.pre_size = [width, height]
        else:
            self.resize(*self.pre_size)  # 若主界面已为最大尺寸，则将其恢复到最大化之前的尺寸
    
    def slot_userLoginBtn_clicked(self):
        """用户登录按钮（表现为用户头像）单击时的槽函数。
        """    
        # 如果未登录
        if not self.is_login:
            login_dialog = MyLoginDialog()
            login_dialog.my_app_sql.update_user_info_signal.connect(self.slot_update_user_info_signal)
            login_dialog.exec_()
        else:  # 如果已登录
            check_msgbox = MyMessageBox(self, '您确定要退出登录吗？')
            if check_msgbox.check_clicked:
                self.slot_update_user_info_signal('guest')
    
    def _update_table_widget(self, table_widget, ret):
        """更新界面中表格控件的全部内容。

        Args:
            table_widget (class): 从PyQt5.QtWidgets引入的QTableWidget类。
            ret (list): 表格控件内显示的内容。
        """  
        # 断开cellChanged信号的槽函数，以免将更新误认为修改内容。
        try:
            table_widget.cellChanged.disconnect()  # 信号不一定已连接到槽函数，因此要做异常处理。
        except:
            pass
        # 更新全部内容      
        table_widget.setRowCount(0)  # 将表格行数置0以达到清空现有数据的效果
        if ret:
            table_widget.setRowCount(len(ret))
            for i in range(len(ret)):
                for j in range(len(ret[i])):
                    table_widget.setItem(i, j, QTableWidgetItem(ret[i][j]))
        
    def _update_playlist_combobox_widget(self):
        """更新界面中歌单下拉列表框和歌单列表控件。
        """        
        # 删除除默认歌单外的其他项
        cnt = self.playlistComboBox.count()
        # 正序删除会导致剩余item的index改变，应逆序删除
        for i in reversed(range(1, cnt)):
            self.playlistComboBox.removeItem(i)
            self.userPlaylistWidget.takeItem(i)
        # 添加当前登录的用户的歌单名
        ret = self.my_app_sql.get_user_playlist_name(self.cur_user)
        if not ret:
            return
        for i in ret:
            self.playlistComboBox.addItem(*i)
            item = QListWidgetItem(*i)
            item.setTextAlignment(Qt.AlignCenter)
            self.userPlaylistWidget.addItem(item)
    
    def slot_update_user_info_signal(self, user_name):
        """用户信息更新信号的槽函数。

        Args:
            user_name (str): 用户名。
        """        
        self.is_login = not self.is_login
        self.cur_user = user_name
        # 更新当前登录的用户信息
        self.userNameLbl.setText(user_name if user_name != 'guest' else '游客')
        self.userInfoListWidget.clear()
        user_info = self.my_app_sql.get_user_info(user_name)
        self.userInfoListWidget.addItems(*user_info)
        # 更新当前用户的播放排行表格
        user_play_count_ret = self.my_app_sql.get_user_play_count(user_name)
        self._update_table_widget(self.songRankedTableWidget, user_play_count_ret)
        # 更新当前用户的收藏表格
        user_like_ret = self.my_app_sql.get_user_like(user_name)
        self._update_table_widget(self.userLikeTableWidget, user_like_ret)
        # 更新当前用户的默认歌单表格
        default_user_playlist_ret = self.my_app_sql.get_user_playlist(user_name, '默认歌单')
        self._update_table_widget(self.playlistSongTableWidget, default_user_playlist_ret)
        # 更新当前用户的歌单下拉列表框和歌单列表控件
        self._update_playlist_combobox_widget()
    
    def slot_changeStackedWidgetBtn_clicked(self, index):
        """子界面切换按钮单击时的槽函数。

        Args:
            index (int): 需要切换的子界面的索引。
        """
        if self.stackedWidget.currentIndex() != index:             
            self.stackedWidget.setCurrentIndex(index)
        else:
            self.stackedWidget.setCurrentIndex(0)  # 如果已经切换到对应索引的子界面，再次点击，则切换回默认子界面。
    
    def slot_playOrderBtn_clicked(self):
        """改变歌曲播放顺序按钮单击时的槽函数。
        """        
        # 0: 顺序播放, 1: 随机播放, 2: 列表循环播放 
        qss_name_list = ['sequential_playOrderBtn.qss', 'random_playOrderBtn.qss', 'loop_playOrderBtn.qss']
        qss_style = CommmonHelper.load_qss(
            qss_name_list[self.my_music_player.change_play_order()])
        if qss_style:
            self.playOrderBtn.setStyleSheet(qss_style)  # 加载QSS样式表以设置界面风格
    
    def slot_preSongBtn_clicked(self):
        """上一首歌曲按钮单击时的槽函数。
        """       
        cur_index = self.my_music_player.playlist.currentIndex()
        if cur_index == -1:
            return
        elif cur_index == 0:
            self.my_music_player.playlist.setCurrentIndex(self.my_music_player.playlist.mediaCount() - 1)
        else:
            self.my_music_player.playlist.previous()
    
    def slot_playBtn_clicked(self):
        """音乐播放按钮单击时的槽函数。
        """   
        # 0: StoppedState, 1: PlayingState, 2: PausedState     
        state = self.my_music_player.music_player.state()
        if state == 1:
            self.my_music_player.music_player.pause()
            qss_filename = 'normal_playBtn.qss'
        else:
            self.my_music_player.music_player.play()
            qss_filename = 'pause_playBtn.qss'
        if state != self.my_music_player.music_player.state():  # 如果播放列表为空，点击播放后状态仍为0。
            qss_style = CommmonHelper.load_qss(qss_filename)
            if qss_style:
                self.playBtn.setStyleSheet(qss_style)  # 加载QSS样式表以设置界面风格
    
    def slot_nextSongBtn_clicked(self):
        """下一首歌曲按钮单击时的槽函数。
        """      
        cur_index = self.my_music_player.playlist.currentIndex()
        if cur_index == -1:
            return
        elif cur_index == self.my_music_player.playlist.mediaCount() - 1:
            self.my_music_player.playlist.setCurrentIndex(0)
        else:
            self.my_music_player.playlist.next()
    
    def slot_likeBtn_clicked(self):
        """收藏按钮单击时的槽函数。
        """        
        index = self.my_music_player.playlist.currentIndex()
        if index == -1:
            return
        song_name = self.my_music_player.song_name_list[index]
        self.my_app_sql.add_user_like_song(self.cur_user, song_name)
        self._update_table_widget(self.userLikeTableWidget,
        self.my_app_sql.get_user_like(self.cur_user))
    
    def slot_searchBtn_clicked(self):
        """搜索按钮单击时的槽函数。
        """        
        search_text = self.searchLnedit.text()
        ret = self.my_app_sql.search_music(search_text)
        if type(ret) is str:
            MyMessageBox(self, ret)
            return
        self._update_table_widget(self.searchRetTableWidget, ret)
        if self.stackedWidget.currentIndex() != 4:
            self.stackedWidget.setCurrentIndex(4)  # 切换到搜索结果页
    
    def _add_song_and_play(self, song_name):
        """将指定歌曲添加到播放列表并播放。

        Args:
            song_name (str): 歌曲名。
        """        
        # 添加到播放列表
        self.my_music_player.add_song_to_playlist(song_name)
        self._update_table_widget(self.curPlayTableWidget,
        self.my_app_sql.get_cur_playlist())
        # 播放最新添加的歌曲
        index = self.my_music_player.playlist.mediaCount() - 1
        self.my_music_player.playlist.setCurrentIndex(index)
        if self.my_music_player.music_player.state() != 1:
            self.slot_playBtn_clicked()  # 如果不为播放状态，则点击播放按钮
        # 播放排行中此歌曲播放次数增加1并更新显示
        self.my_app_sql.update_user_play_count(self.cur_user, song_name)
        self._update_table_widget(self.songRankedTableWidget,
        self.my_app_sql.get_user_play_count(self.cur_user))
    
    def slot_recSongBtn_clicked(self, btn, lbl):
        """推荐音乐按钮单击时的槽函数。

        Args:
            btn (QPushButton): 推荐按钮。
            lbl (QLabel): 推荐按钮对应的歌曲名标签。
        """        
        song_name = lbl.text()
        self._add_song_and_play(song_name)
        
    def _select_user_like_song(self, table_widget):
        """获得用户在表格控件中选择的歌曲名。

        Args:
            table_widget (QTableWidget): 从PyQt5.QtWidgets引入的QTableWidget类。

        Returns:
            list or None: 用户选择的歌曲名列表。
        """        
        items = table_widget.selectedItems()
        if items == []:
            MyMessageBox(self, '请选择歌曲再进行操作！')
            return None
        row = []
        for i in items:
            row.append(i.row())
        row = list(set(row))  # 去除重复元素
        song_name = [table_widget.item(i, 0).text() for i in row]
        return song_name
    
    def slot_addToPlaylistBtn_clicked(self):
        """添加到歌单按钮单击时的槽函数。
        """
        song_name = self._select_user_like_song(self.userLikeTableWidget)
        if not song_name:
            return
        playlist_name = self.playlistComboBox.currentText()
        self.my_app_sql.add_to_playlist(self.cur_user, playlist_name, song_name)
        # 更新当前歌单的歌曲详情
        item = self.userPlaylistWidget.currentItem()
        if item is not None:
            self.slot_user_playlist_item_clicked(item)
        else:
            self.slot_user_playlist_item_clicked(self.userPlaylistWidget.item(0))  # 默认歌单
        MyMessageBox(self, '歌曲添加完毕！')
    
    def slot_delLikeSongBtn_clicked(self):
        """从收藏中移除按钮单击时的槽函数。
        """       
        song_name = self._select_user_like_song(self.userLikeTableWidget)
        if not song_name:
            return
        self.my_app_sql.del_user_like_song(self.cur_user, song_name)
        self._update_table_widget(self.userLikeTableWidget,
        self.my_app_sql.get_user_like(self.cur_user))
        MyMessageBox(self, '选中的歌曲已从收藏中移除！')

    def slot_createPlaylistBtn_clicked(self):
        """创建歌单按钮单击时的槽函数。
        """        
        create_playlist_dialog = MyCreatePlaylistDialog(self.cur_user)
        create_playlist_dialog.my_app_sql.update_playlist_signal.connect(self.slot_update_playlist_signal)
        create_playlist_dialog.exec_()
    
    def slot_update_playlist_signal(self, playlist_name):
        """歌单信息更新信号的槽函数。

        Args:
            playlist_name (str): 歌单名。
        """ 
        # 添加到用户歌单列表控件
        item = QListWidgetItem(playlist_name)
        item.setTextAlignment(Qt.AlignCenter)
        self.userPlaylistWidget.addItem(item)
        # 添加到歌单下拉列表框
        self.playlistComboBox.addItem(playlist_name)
    
    def slot_delPlaylistBtn_clicked(self):
        """删除歌单按钮单击时的槽函数。
        """        
        index_selected = self.userPlaylistWidget.currentRow()
        if index_selected < 0:
            MyMessageBox(self, '请选择需要删除的歌单！')
            return
        elif index_selected == 0:
            MyMessageBox(self, '不能删除默认歌单！')
            return
        else:
            playlist_name = self.userPlaylistWidget.currentItem().text()
            # 从数据库中删除歌单
            self.my_app_sql.del_playlist(self.cur_user, playlist_name)
            # 从歌单下拉列表框和歌单列表控件中删除歌单
            self.userPlaylistWidget.takeItem(index_selected)
            cnt = self.playlistComboBox.count()
            for i in range(1, cnt):
                if self.playlistComboBox.itemText(i) == playlist_name:
                    self.playlistComboBox.removeItem(i)
                    break
            MyMessageBox(self, '歌单删除成功！')
    
    def _add_single_song(self, file_path, file_type):
        """添加单首歌曲。

        Args:
            file_path (str): 选择的文件路径。
            file_type (str)): 文件类型。

        Returns:
            str: 未能成功完成添加歌词和封面图片操作的歌曲名。
        """        
        file_name = (file_path.split('/')[-1]).split('.')[0]
        # 获取歌曲名和演唱者名（如有）
        singer_name = None
        if '-' in file_name:
            song_name = file_name.split('-')[0]
            singer_name = file_name.split('-')[-1]
        else:
            song_name = file_name
        is_exist = bool(self.my_app_sql.search_music(song_name, is_strict=True))
        # 根据不同的文件类型执行不同的操作
        if file_type == '音乐文件(*.mp3 *.wav)':
            # 若数据库中已存在该歌曲，则更新歌曲路径，否则新增一条歌曲信息。
            if is_exist:
                self.my_app_sql.change_music_info(song_name, 'song_path', file_path)
            else:
                self.my_app_sql.add_local_music(song_name, file_path)
            if singer_name:
                self.my_app_sql.change_music_info(song_name, 'singer_name', singer_name)
        elif file_type == '歌词文件(*.lrc)' or file_type == '封面图片文件(*.jpg *.jepg *.png *.bmp *.webp)':
            # 歌曲已存在时，才能添加歌词文件。
            if is_exist:
                column_name = 'song_lyric_path' if file_type == '歌词文件(*.lrc)' else 'song_cover_path'
                self.my_app_sql.change_music_info(song_name, column_name, file_path)
                if singer_name:
                    self.my_app_sql.change_music_info(song_name, 'singer_name', singer_name)
            else:
                return song_name  # 返回因为不存在而无法添加歌词和封面图片的歌曲名

    def slot_addSongBtn_clicked(self):
        """添加歌曲按钮单击时的槽函数。
        """        
        files_path, file_type = QFileDialog.getOpenFileNames(self, '选择要添加的音乐',
        parentpath, '音乐文件(*.mp3 *.wav);;歌词文件(*.lrc);;封面图片文件(*.jpg *.jepg *.png *.bmp *.webp)')
        if len(files_path) == 0:
            return
        prompt = []
        for i in files_path:
            ret = self._add_single_song(i, file_type)
            if ret:
                prompt.append(ret)
        if prompt:
            prompt = ''.join(['以下歌曲请先添加音乐文件再添加歌词和封面图片文件：\n', '，'.join(prompt)])
            MyMessageBox(self, prompt)
        self.show_music()  # 更新本地音乐表格控件
    
    def slot_delSongBtn_clicked(self):
        """删除歌曲按钮单击时的槽函数。
        """        
        song_name = self._select_user_like_song(self.localMusicTableWidget)
        if not song_name:
            return
        for i in song_name:
            self.my_app_sql.del_local_music(i)
        prompt = ''.join(['以下歌曲已被成功删除：\n', '，'.join(song_name)])
        MyMessageBox(self, prompt)
        # 更新播放列表
        self.my_music_player.remove_song_from_playlist(song_name)
        # 更新表格控件
        self._update_table_widget(self.curPlayTableWidget,
        self.my_app_sql.get_cur_playlist())
        self._update_table_widget(self.songRankedTableWidget,
        self.my_app_sql.get_user_play_count(self.cur_user))
        self._update_table_widget(self.userLikeTableWidget,
        self.my_app_sql.get_user_like(self.cur_user))
        item = self.userPlaylistWidget.currentItem()
        if item is not None:
            self.slot_user_playlist_item_clicked(item)
        else:
            self.slot_user_playlist_item_clicked(self.userPlaylistWidget.item(0))  # 默认歌单
        self.show_music()
    
    def slot_user_playlist_item_clicked(self, item: QListWidgetItem):
        """用户歌单列表控件中的项目单击时的槽函数。切换到相应歌单的歌曲详情。

        Args:
            item (QListWidgetItem): 用户歌单列表控件中的项目。
        """        
        playlist_name = item.text()
        # 更新歌单详情
        ret = self.my_app_sql.get_user_playlist(self.cur_user, playlist_name)
        self._update_table_widget(self.playlistSongTableWidget, ret)
    
    def slot_table_widget_cell_clicked(self, row, column, table_widget, start=0):
        """表格控件中单元格单击时的槽函数。单击时将该表格控件的内容更改信号连接到槽函数。

        Args:
            row (int): 被单击的单元格的行。
            column (int): 被单击的单元格的列。
            table_widget (QTableWidget): 从PyQt5.QtWidgets引入的QTableWidget类。
            start (int, optional): 歌曲名所在的列。 Defaults to 0.
        """        
        table_widget.cellChanged.connect(lambda row, column:
        self.slot_table_widget_cell_changed(row, column, table_widget=table_widget, start=start))
    
    def slot_table_widget_cell_changed(self, row, column, table_widget, start):
        """表格控件中单元格内容更改时的槽函数。

        Args:
            row (int): 被更改的单元格的行。
            column (int): 被更改的单元格的列。
            table_widget (QTableWidget): 从PyQt5.QtWidgets引入的QTableWidget类。
            start (int, optional): 歌曲名所在的列。 Defaults to 0.
        """        
        changed_column = ['singer_name', 'album_name', 'song_lan']  # 能改的有：演唱者，专辑名，语言。
        song_name = table_widget.item(row, start).text()
        changed_text = table_widget.item(row, column).text()
        # 将更改写入数据库
        if (column - start - 1) >= len(changed_column):
            # 这种是由于歌曲持续时间更新触发的信号，应当断开当前信号与槽函数的连接并直接退出。
            table_widget.cellChanged.disconnect()
            return
        self.my_app_sql.change_music_info(song_name, changed_column[column - start - 1], changed_text)
        # 同步更新到其他表格控件
        if table_widget != self.curPlayTableWidget:
            cnt = self.curPlayTableWidget.rowCount()
            for i in range(cnt):
                if self.curPlayTableWidget.item(i, 0).text() == song_name:
                    self.curPlayTableWidget.setItem(i, column - start, QTableWidgetItem(changed_text))
        
        if table_widget != self.songRankedTableWidget:
            cnt = self.songRankedTableWidget.rowCount()
            for i in range(cnt):
                if self.songRankedTableWidget.item(i, 1).text() == song_name:
                    self.songRankedTableWidget.setItem(i, column - start + 1, QTableWidgetItem(changed_text))

        if table_widget != self.userLikeTableWidget:
            cnt = self.userLikeTableWidget.rowCount()
            for i in range(cnt):
                if self.userLikeTableWidget.item(i, 0).text() == song_name:
                    self.userLikeTableWidget.setItem(i, column - start, QTableWidgetItem(changed_text))

        if table_widget != self.playlistSongTableWidget:
            cnt = self.playlistSongTableWidget.rowCount()
            for i in range(cnt):
                if self.playlistSongTableWidget.item(i, 0).text() == song_name:
                    self.playlistSongTableWidget.setItem(i, column - start, QTableWidgetItem(changed_text))

        if table_widget != self.localMusicTableWidget:
            cnt = self.localMusicTableWidget.rowCount()
            for i in range(cnt):
                if self.localMusicTableWidget.item(i, 0).text() == song_name:
                    self.localMusicTableWidget.setItem(i, column - start, QTableWidgetItem(changed_text))

        if table_widget != self.searchRetTableWidget:
            cnt = self.searchRetTableWidget.rowCount()
            for i in range(cnt):
                if self.searchRetTableWidget.item(i, 0).text() == song_name:
                    self.searchRetTableWidget.setItem(i, column - start, QTableWidgetItem(changed_text))
        # 断开当前信号与槽函数的连接
        table_widget.cellChanged.disconnect()
    
    def slot_update_song_duration_signal(self, content):
        """歌曲持续时间更新信号的槽函数。

        Args:
            content (list): [str: 歌曲名, int: 总毫秒, str: 时分秒]
        """     
        song_name, value, time_text = content 
        # 更新播放标签
        self.curSongLbl.setText(f"  正在播放：{song_name}")
        self.playCurTimeLbl.setText('00:00:00')
        self.playEndTimeLbl.setText(time_text)
        self.lyricLbl.setText('')  # 清空现有歌词
        # 更新滑动条控件  
        self.playHorizontalSlider.setRange(0, value) 
        self.playHorizontalSlider.setEnabled(True)  # 音乐开始播放时允许滑动条
        # 更新表格控件中歌曲的持续时间
        get_index = lambda table_widget: [table_widget.rowCount(), table_widget.columnCount()]
        row_cnt, column_cnt = get_index(self.curPlayTableWidget)
        for i in range(row_cnt):
            if self.curPlayTableWidget.item(i, 0).text() == song_name:
                self.curPlayTableWidget.setItem(i, column_cnt - 1, QTableWidgetItem(time_text))

        row_cnt, column_cnt = get_index(self.songRankedTableWidget)
        for i in range(row_cnt):
            if self.songRankedTableWidget.item(i, 0).text() == song_name:
                self.songRankedTableWidget.setItem(i, column_cnt - 1, QTableWidgetItem(time_text))

        row_cnt, column_cnt = get_index(self.userLikeTableWidget)
        for i in range(row_cnt):
            if self.userLikeTableWidget.item(i, 0).text() == song_name:
                self.userLikeTableWidget.setItem(i, column_cnt - 1, QTableWidgetItem(time_text))

        row_cnt, column_cnt = get_index(self.playlistSongTableWidget)
        for i in range(row_cnt):
            if self.playlistSongTableWidget.item(i, 0).text() == song_name:
                self.playlistSongTableWidget.setItem(i, column_cnt - 1, QTableWidgetItem(time_text))

        row_cnt, column_cnt = get_index(self.localMusicTableWidget)
        for i in range(row_cnt):
            if self.localMusicTableWidget.item(i, 0).text() == song_name:
                self.localMusicTableWidget.setItem(i, column_cnt - 1, QTableWidgetItem(time_text))

        row_cnt, column_cnt = get_index(self.searchRetTableWidget)
        for i in range(row_cnt):
            if self.searchRetTableWidget.item(i, 0).text() == song_name:
                self.searchRetTableWidget.setItem(i, column_cnt - 1, QTableWidgetItem(time_text))
    
    def slot_update_song_position_signal(self, content):
        """歌曲播放位置更新信号的槽函数。

        Args:
            content (list): [str: 歌曲名, int: 总毫秒, str: 时分秒]
        """        
        song_name, value, time_text = content 
        # 更新时间标签
        self.playCurTimeLbl.setText(time_text)
        # 更新滑动条
        self.playHorizontalSlider.setValue(value)
        # 更新歌词
        try:
            self.lyricLbl.setText(self.my_music_player.song_lyric_dict[song_name][time_text])
        except:
            pass   
    
    def slot_song_end_signal(self, content):
        """歌曲（因删除）终止信号的槽函数。

        Args:
            content (str): 提示语（目前没用上）。
        """        
        # 初始化播放标签
        self.curSongLbl.setText("  正在播放：")
        self.playCurTimeLbl.setText('00:00:00')
        self.playEndTimeLbl.setText('00:00:00')
        self.lyricLbl.setText('')  # 清空现有歌词
        # 禁止滑动条控件  
        self.playHorizontalSlider.setValue(0)
        self.playHorizontalSlider.setEnabled(False)  # 音乐终止时禁止滑动条
        # 播放按钮视为初始状态
        self.my_music_player.music_player.pause()
        qss_filename = 'normal_playBtn.qss'
        qss_style = CommmonHelper.load_qss(qss_filename)
        if qss_style:
            self.playBtn.setStyleSheet(qss_style)  # 加载QSS样式表以设置界面风格

    def slot_sliderMoved(self, value):
        """滑动条滑动时的槽函数。

        Args:
            value (int): 滑动条的值。
        """        
        self.my_music_player.music_player.setPosition(value)  # 歌曲播放位置相应变动

    def slot_table_widget_cell_doubleclicked(self, row, column, table_widget, start=0):
        """表格控件中单元格双击时的槽函数。

        Args:
            row (int): 被双击的单元格的行。
            column (int): 被双击的单元格的列。
             table_widget (QTableWidget): 从PyQt5.QtWidgets引入的QTableWidget类。
             start (int, optional): 歌曲名所在的列。 Defaults to 0.
        """        
        song_name = table_widget.item(row, start).text()
        self._add_song_and_play(song_name)
