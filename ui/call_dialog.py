import sys
import os
curpath = os.path.abspath(os.path.dirname(__file__))
parentpath = os.path.abspath(os.path.dirname(curpath))
sys.path.append(parentpath)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QCursor
from ui.common_helper import CommmonHelper
from service.app_sql import AppSQL

class MyDialog(QDialog):
    """自定义QDialog类。

    Args:
        QDialog (class): 从PyQt5.QtWidgets引入的QDialog类。
    """    

    def __init__(self, qss_filename):
        """初始化。

        Args:
            qss_filename (str): QSS样式表文件名。
        """        
        super().__init__(parent=None)
        self._init_dialog()
        qss_style = CommmonHelper.load_qss(qss_filename)
        if qss_style:
            self.setStyleSheet(qss_style)  # 加载QSS样式表以设置界面风格
        self._init_global_variable()
    
    def _init_dialog(self):
        """设置界面的某些显示效果。
        """
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置界面无边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置界面背景透明
        self.setAttribute(Qt.WA_NoSystemBackground, False)  # 使界面背景透明不影响border-image绘制
    
    # 使界面在无边框的情况下可以拖曳移动
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
    
    def _init_global_variable(self):
        """预设部分需要使用的全局变量。
        """
        self.my_app_sql = AppSQL()
