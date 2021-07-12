import sys
import os
curpath = os.path.abspath(os.path.dirname(__file__))
parentpath = os.path.abspath(os.path.dirname(curpath))
sys.path.append(parentpath)
from PyQt5.QtWidgets import QMessageBox
from ui.common_helper import CommmonHelper

class MyMessageBox(QMessageBox):
    """自定义消息框类。

    Args:
        QMessageBox (class): 从PyQt5.QtWidgets引入的QMessageBox类。
    """    

    def __init__(self, parent, text, title='提示', icon_type='信息', btn_num=1):
        """MyMessageBox类的初始化函数。

        Args:
            parent (class): 消息框的父窗口。
            text (str): 消息框提示语。
            title (str, optional): 消息框标题。 Defaults to '提示'.
            icon_type (str, optional): 消息框提示图标。 Defaults to '信息'.
            btn_num (int, optional): 消息框按钮个数图标。 Defaults to 1.
        """        
        super().__init__(parent)
        self.msgbox = QMessageBox()  # 实例化消息框
        self.init_msgbox(text, title, icon_type, btn_num)  # 设置消息框的控件和样式
        self.show()
    
    def init_msgbox(self, text, title, icon_type, btn_num):
        """设置消息框的控件和样式。

        Args:
            text (str): 消息框提示语。
            title (str): 消息框标题。
            icon_type (str): 消息框提示图标。
            btn_num (int): 消息框按钮个数图标。
        """        
        self.msgbox.setWindowTitle(title)  # 设置标题
        self.msgbox.setText(text)  # 设置提示语
        icon_type_dict = {'关于': 0, '信息': 1, '警告': 2, '危险': 3, '询问': 4}
        self.msgbox.setIcon(icon_type_dict[icon_type])  # 设置提示图标
        # 设置按钮
        if btn_num == 1:  # 仅需要确认按钮
            self.msgbox.setStandardButtons(QMessageBox.Yes)
        elif btn_num == 2:  # 需要确认和取消按钮
            self.msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            self.cancelBtn = self.msgbox.button(QMessageBox.Cancel)
            self.cancelBtn.setText('  取消  ')
        self.yesBtn = self.msgbox.button(QMessageBox.Yes)
        self.yesBtn.setText('  确定  ')
        qss_filename = 'default_ui_msgbox.qss'
        qss_style = CommmonHelper.load_qss(qss_filename)
        if qss_style:
            self.msgbox.setStyleSheet(qss_style)  # 加载QSS样式表以设置界面风格
    
    def show(self):
        """显示消息框。
        """        
        self.msgbox.exec_()
        self.check_clicked = (self.msgbox.clickedButton() == self.yesBtn)  # 是否点击确定
