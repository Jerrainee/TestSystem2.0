from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QTableWidget


class ShowProfileResults(QMainWindow):
    def __init__(self, con, cur, user):
        super().__init__()
        uic.loadUi('interface/ProfileResultsInterface.ui', self)
        self.con = con
        self.cur = cur
        self.user = user
        self.initUI()

    def initUI(self):
        self.SearchPB.clicked.connect(self.search_test)
        self.UpdatePB.clicked.connect(self.default_query)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.default_query()

    def default_query(self):
        self.query = f'''Select Test_id, Test_name, Subjects.subject, Result, Date, User_answers From Log
                         left join Subjects 
                         on Log.Test_subject_id = Subjects.Subject_ID 
                         where Log.User_login = ?'''
        data = self.cur.execute(self.query, (self.user.login,)).fetchall()
        self.result_update(data)

    def result_update(self, data):
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(data):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                if j % 5 == 0:
                    self.tableWidget.setItem(i, j, QTableWidgetItem(', '.join((str(elem)).split(';;'))))
                else:
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()

    def search_test(self):
        text = str(self.SearchStr.text())
        lst1 = ['Названию', 'Id', 'Предмету']
        lst2 = ['Test_name', 'Test_id', 'Subjects.Subject']
        column = str(lst2[lst1.index(self.SearchCB.currentText())])
        cur_query = self.query + f" and {column} like '%{text}%'"
        data = self.cur.execute(cur_query, (self.user.login,)).fetchall()
        self.result_update(data)
