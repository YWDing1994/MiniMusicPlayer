import sys
import os
curpath = os.path.abspath(os.path.dirname(__file__))
parentpath = os.path.abspath(os.path.dirname(curpath))
sys.path.append(parentpath)
from ui.call_dialog import MyDialog
from ui.Ui_create_playlist_dialog import Ui_createPlaylistDialog
from ui.call_message_box import MyMessageBox

class MyCreatePlaylistDialog(MyDialog, Ui_createPlaylistDialog):
    """根据UI设计和业务逻辑设置创建歌单界面。

    Args:
        QDialog (class): 从PyQt5.QtWidgets引入的QDialog类。
        Ui_createPlaylistDialog (class): 创建歌单界面的UI设计类。
    """  

    def __init__(self, user_name):
        super().__init__(qss_filename='default_ui_create_playlist_dialog.qss')
        self.setupUi(self)
        self.cur_user = user_name
        self.init_slot_func()
    
    
    def init_slot_func(self):
        """设置创建歌单界面各控件的槽函数。
        """
        # 关闭按钮，取消按钮
        self.closeBtn.clicked.connect(self.close)
        self.cancelBtn.clicked.connect(self.close)
        # 确定按钮
        self.okBtn.clicked.connect(self.slot_okBtn_clicked)
        # 创建歌单时的信号
        self.my_app_sql.create_playlist_dialog_signal.connect(self.slot_create_playlist_dialog_signal)
    
    def get_create_playlist_dialog_input(self):
        """获取创建歌单界面的输入。

        Returns:
            str: playlist_name。
        """           
        playlist_name = self.userPlaylistLnedit.text()                   
        return playlist_name

    def slot_okBtn_clicked(self):
        """确定按钮单击时的槽函数。
        """   
        playlist_name = self.get_create_playlist_dialog_input()     
        self.my_app_sql.create_playlist(self.cur_user, playlist_name)
    
    def slot_create_playlist_dialog_signal(self, content: str):
        """创建歌单时的信号的槽函数。提示操作结果。

        Args:
            content (str): 操作结果提示语。
        """        
        MyMessageBox(self, content)
        if content == '歌单创建成功！':
            self.close()
    