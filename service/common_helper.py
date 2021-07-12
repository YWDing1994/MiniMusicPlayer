import sys
import os
curpath = os.path.abspath(os.path.dirname(__file__))
parentpath = os.path.abspath(os.path.dirname(curpath))
sys.path.append(parentpath)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

class CommmonHelper(object):
    """功能帮助类。该类中封装了一些常用的公共方法。
    """

    def __init__(self):
        pass

    @staticmethod
    def load_sql(sql_filename):
        """导入需要执行的SQL文件。

        Args:
            sql_filename (str, optional): SQL文件名。 Defaults to 'create_db.sql'.

        Returns:
            list: SQL文件中的每一条语句。
        """        
        sql_filepath = '/'.join([parentpath.replace('\\', '/'), 'dao/db', sql_filename])
        with open(sql_filepath, 'r+', encoding='utf-8') as f:
            sql_list = f.read().split(';')[:-1]
            sql_list = [x.replace('\n', ' ') if '\n' in x else x for x in sql_list]
            return sql_list

class CommonSQL(object):
    """通用SQL类。
    """    

    def __init__(self):
        pass

    def __enter__(self):
        self.connect_db()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db.commit()
        self.db.close()
    
    def run_sql(self, sql_filename):
        """执行指定的SQL文件。

        Args:
            sql_filename (str): 需要执行的SQL文件名。
        """        
        for i in CommmonHelper.load_sql(sql_filename):
            self.sql_query.exec_(i)

    def connect_db(self, db_name='minimusicplayer_db.db'):
        """连接到指定数据库。

        Args:
            db_name (str, optional): 数据库名。若数据库不存在，则按预定规则创建。 Defaults to 'minimusicplayer_db.db'.
        """        
        db_path = '/'.join([parentpath.replace('\\', '/'), 'dao/db', db_name])
        is_db_exist = os.path.exists(db_path)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(db_path)
        self.db.open()
        self.sql_query = QSqlQuery()
        if not is_db_exist:
            self.run_sql('create_db.sql')  # 如果该数据库不存在，则导入SQL文件并执行以创建数据库。
    
    def get_table_column_name(self, table_name):
        """获取指定表的所有字段名。

        Args:
            table_name (str): 指定表的表名。

        Returns:
            list: 包含指定表的所有字段名的列表。
        """        
        sql = f"PRAGMA TABLE_INFO([{table_name}])"
        self.sql_query.exec_(sql)
        column_name = []
        while self.sql_query.next():
            column_name.append(self.sql_query.value(1))  # 当value的参数为0时得到的是每个字段的序号
        return column_name
    
    def common_sql(self, *args, sql, is_select=False):
        """通用的执行SQL语句函数。

        Args:
            sql (str): 需要执行的SQL语句。
            is_select (bool, optional): 是否为查询语句。 Defaults to False.

        Returns:
            int or None: 结果集中的记录条数（仅用于查询语句）。
        """        
        self.sql_query.prepare(sql)
        for i in range(len(args)):
            self.sql_query.bindValue(i, args[i])
        self.sql_query.exec_()
        if is_select:
            ret_num = 0  # 结果集中的记录条数
            if self.sql_query.last():
                ret_num = self.sql_query.at() + 1
                self.sql_query.first()
                self.sql_query.previous()  # 回到第“0'条记录，以便next函数使用
            return ret_num
