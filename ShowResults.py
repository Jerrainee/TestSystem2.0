from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QTableWidget


class ShowResults(QMainWindow):
    def __init__(self, con, cur):
        super().__init__()
        uic.loadUi('interface/ResultInterface.ui', self)
        self.con = con
        self.cur = cur
        self.initUI()

    def initUI(self):
        self.SearchPB.clicked.connect(self.search_test)
        self.UpdatePB.clicked.connect(self.default_query)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.default_query()

    def default_query(self):
        self.query = '''Select User_login, Test_id, Test_name, Subjects.subject, Result, Date From log
                        left join Subjects 
                        on Log.Test_subject_id = Subjects.Subject_ID'''
        data = self.cur.execute(self.query).fetchall()
        self.result_update(data)

    def result_update(self, data):
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(data):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()

    def search_test(self):
        text = str(self.SearchStr.text())
        lst1 = ['Пользователю', 'Названию', 'Id теста', 'Предмету']
        lst2 = ['User_login', 'Test_name', 'Test_id', 'Subjects.Subject']
        column = str(lst2[lst1.index(self.SearchCB.currentText())])
        cur_query = self.query + f" where {column} like '%{text}%'"
        data = self.cur.execute(cur_query)
        self.result_update(data)
