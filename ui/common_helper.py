import os
from PyQt5.QtWidgets import QStyledItemDelegate, QTableWidget

class CommmonHelper(object):
    """功能帮助类。该类中封装了一些常用的公共方法。
    """

    def __init__(self):        
        pass

    @staticmethod
    def load_qss(qss_filename):
        """导入QSS样式表。

        Args:
            qss_filename (str): QSS样式表文件名。

        Returns:
            str: 读取的QSS样式表。
            None: 读取异常时返回None。
        """      
        qss_filepath = '/'.join([os.path.dirname(os.path.abspath(__file__)).replace('\\', '/'), 'qss', qss_filename])
        try:
            with open(qss_filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None

class ReadOnlyDelegate(QStyledItemDelegate):
    """设置表格控件不可编辑行或列的辅助类。

    Args:
        QStyledItemDelegate (class): 从PyQt5.QtWidgets引入的QStyledItemDelegate类。
    """    

    def createEditor(self, parent, option, index):
        return

class SetQTableWidgetEditable(object):
    """设置表格控件不可编辑行或列的类。
    """    

    def __init__(self):
        pass
    
    @staticmethod
    def set_column(table_widget: QTableWidget, column_index):
        """设置指定表格控件的不可编辑列。

        Args:
            table_widget (QTableWidget): 指定的表格控件。
            column_index (list): 不可编辑列。
        """        
        delegate = ReadOnlyDelegate(table_widget)
        for i in column_index:
            table_widget.setItemDelegateForColumn(i, delegate)
    
    @staticmethod
    def set_row(table_widget: QTableWidget, row_index):
        """设置指定表格控件的不可编辑行。

        Args:
            table_widget (QTableWidget): 指定的表格控件。
            row_index (list): 不可编辑行。
        """        
        delegate = ReadOnlyDelegate(table_widget)
        for i in row_index:
            table_widget.setItemDelegateForRow(i, delegate)
