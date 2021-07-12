import sys
import os
curpath = os.path.abspath(os.path.dirname(__file__))
parentpath = os.path.abspath(os.path.dirname(curpath))
sys.path.append(parentpath)
from ui.call_dialog import MyDialog
from ui.Ui_login_dialog import Ui_loginDialog
from ui.call_register_dialog import MyRegisterDialog
from ui.call_message_box import MyMessageBox

class MyLoginDialog(MyDialog, Ui_loginDialog):
    """根据UI设计和业务逻辑设置登录界面。

    Args:
        QDialog (class): 从PyQt5.QtWidgets引入的QDialog类。
        Ui_loginDialog (class): 登录界面的UI设计类。
    """    

    def __init__(self):
        super().__init__(qss_filename='default_ui_login_dialog.qss')
        self.setupUi(self)
        self.init_slot_func()
    
    def init_slot_func(self):
        """设置登录界面各控件的槽函数。
        """
        # 关闭按钮
        self.closeBtn.clicked.connect(self.close)
        # 账号登录按钮
        self.loginBtn.clicked.connect(self.slot_loginBtn_clicked)
        # 账号注册按钮
        self.registerBtn.clicked.connect(self.slot_registerBtn_clicked)
        # 账号登录时的信号
        self.my_app_sql.login_dialog_signal.connect(self.slot_login_dialog_signal)
    
    def get_login_dialog_input(self):
        """获取登录界面的输入。

        Returns:
            tuple: (user_name, password)
        """        
        user_name = self.userNameLnedit.text()
        password = self.pwdLnedit.text()
        return user_name, password
    
    def slot_loginBtn_clicked(self):
        """账号登录按钮单击时的槽函数。
        """
        user_name, password = self.get_login_dialog_input()
        self.my_app_sql.login(user_name, password)
    

    def slot_login_dialog_signal(self, content: str):
        """账号登录时的信号的槽函数。提示操作的结果。

        Args:
            content (str): 操作结果提示语。
        """        
        MyMessageBox(self, content)
        if content == '登录成功！':
            self.close()     
    
    def slot_registerBtn_clicked(self):
        """账号注册按钮单击时的槽函数。
        """    
        register_dialog =  MyRegisterDialog()
        register_dialog.exec_()
        