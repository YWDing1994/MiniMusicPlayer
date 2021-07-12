import sys
import os
curpath = os.path.abspath(os.path.dirname(__file__))
parentpath = os.path.abspath(os.path.dirname(curpath))
sys.path.append(parentpath)
from ui.call_dialog import MyDialog
from ui.Ui_register_dialog import Ui_registerDialog
from ui.call_message_box import MyMessageBox

class MyRegisterDialog(MyDialog, Ui_registerDialog):
    """根据UI设计和业务逻辑设置注册界面。

    Args:
        QDialog (class): 从PyQt5.QtWidgets引入的QDialog类。
        Ui_registerDialog (class): 注册界面的UI设计类。
    """    

    def __init__(self):
        super().__init__(qss_filename='default_ui_register_dialog.qss')
        self.setupUi(self)
        self.init_slot_func()
    
    def init_slot_func(self):
        """设置注册界面各控件的槽函数。
        """
        # 关闭按钮
        self.closeBtn.clicked.connect(self.close)
        # 注册账号按钮, 修改密码按钮
        self.registerBtn.clicked.connect(
            lambda: self.slot_registerBtn_or_changePwdBtn_clicked(chosen_tpye='register'))
        self.changePwdBtn.clicked.connect(
            lambda: self.slot_registerBtn_or_changePwdBtn_clicked(chosen_tpye='change_password'))
        # 注册账号或修改密码时的信号
        self.my_app_sql.register_dialog_signal.connect(self.slot_register_dialog_signal)
    
    def get_register_dialog_input(self):
        """获取注册界面的输入。

        Returns:
            tuple: (user_name, password, check_password)
        """        
        user_name = self.userNameLnedit.text()
        password = self.pwdLnedit.text()
        check_password = self.checkPwdLnedit.text()
        return user_name, password, check_password
    
    def slot_registerBtn_or_changePwdBtn_clicked(self, chosen_tpye):
        """注册账号或修改密码按钮单击时的槽函数。

        Args:
            chosen_tpye (str): 操作类型。register或change_password。
        """        
        user_name, password, check_password = self.get_register_dialog_input()
        self.my_app_sql.register_or_change_password(user_name, password, check_password, chosen_tpye)
    
    def slot_register_dialog_signal(self, content: str):
        """注册账号或修改密码时的信号的槽函数。提示操作的结果。

        Args:
            content (str): 操作结果提示语。
        """        
        MyMessageBox(self, content)
        if content == '恭喜您，注册成功！' or content == '修改密码成功！':
            self.close()
