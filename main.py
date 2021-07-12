import sys
import os
curpath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(curpath)
from PyQt5.QtWidgets import QApplication
from ui.call_main_window import MyMainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_main_window = MyMainWindow()
    my_main_window.show()
    sys.exit(app.exec_())
