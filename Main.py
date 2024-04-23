import sys

import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QInputDialog, QMessageBox, QTableWidget

from AddTest import AddTest
from DeleteTest import DeleteTest
from EditSubject import EditSubject
from ShowResults import ShowResults
from TestRun import TestRun


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface/Main_Interface.ui', self)
        self.initUI()

    def initUI(self):
        self.account = ''
        self.mbox = QMessageBox(self)
        self.UpdatePB.clicked.connect(self.default_query)
        self.AdminPB.clicked.connect(self.for_admin)
        self.AdminPB.hide()
        self.LoginPB.clicked.connect(self.log_in_account)
        self.SortingCB.currentTextChanged.connect(self.sort_table)
        self.SearchPB.clicked.connect(self.search_test)
        self.tableWidget.itemDoubleClicked.connect(self.check_account)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.con = sqlite3.connect('db/TestSystemDB.db3')
        self.cur = self.con.cursor()
        self.RowsLst = []
        self.default_query()

    def default_query(self):
        self.query = """ Select Id, Name, Subject From Tests
                         left join Subjects 
                         on Tests.Subject_ID = Subjects.Subject_ID"""
        data = self.cur.execute(self.query).fetchall()
        self.update_table(data)

    def update_table(self, data):
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(data):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.RowsLst.append(row)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()

    def search_test(self):
        text = str(self.SearchStr.text())
        lst1 = ['Id', 'Названию', 'Предмету']
        lst2 = ['tests.ID', 'tests.Name', 'Subjects.Subject']
        column = str(lst2[lst1.index(self.SearchCB.currentText())])
        self.query += f" where {column} like '%{text}%'"
        data = self.cur.execute(self.query)
        self.update_table(data)

    def for_admin(self):
        request, ok_pressed = QInputDialog.getItem(
            self, 'Меню', 'Выберите дейсвие:',
            ('Редактировать тест', 'Редактировать предмет', 'Посмотреть результаты'), 0, False)
        if ok_pressed:
            if request == 'Редактировать тест':
                request, ok_pressed = QInputDialog.getItem(
                    self, 'Меню', 'Выберите дейсвие:',
                    ('Добавить тест', 'Удалить тест'), 0, False)
                if ok_pressed:
                    if request == 'Добавить тест':
                        self.dialog = AddTest(self.con, self.cur)
                        self.dialog.show()
                    if request == 'Удалить тест':
                        self.dialog = DeleteTest(self.con, self.cur, self.RowsLst)
            if request == 'Редактировать предмет':
                self.dialog = EditSubject(self.con, self.cur)
            if request == 'Посмотреть результаты':
                self.dialog = ShowResults(self.con, self.cur)
                self.dialog.show()

    def sort_table(self):
        lst1 = ['Id', 'Названию', 'Предмету']
        column = lst1.index(self.SortingCB.currentText())
        self.tableWidget.sortItems(column)

    def check_account(self):
        if self.account == '':
            valid = QMessageBox.question(
                self, '', 'Вы не вошли в аккаунт, результат прохождения не будет засчитан. Продолжить?',
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                self.test_run()
        else:
            self.test_run()

    def test_run(self):
        row = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        Id, Name = self.RowsLst[row[0]][0], self.RowsLst[row[0]][1]
        valid = QMessageBox.question(
            self, '', f'Вы уверенны, что хотите начать прохождение данного теста: {Name}?',
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            self.dialog = TestRun(self.con, self.cur, self.RowsLst, self.account, Id, Name)
            self.dialog.show()

    def log_in_account(self):
        login, ok_pressed = QInputDialog.getText(self, "Аккаунт",
                                                 "Пожалуйста, введите ваш логин:")
        if ok_pressed and login:
            query = '''Select login From accounts where login = ?'''
            data = self.cur.execute(query, (login,)).fetchall()
            if data:
                password, ok_pressed = QInputDialog.getText(self, "Аккаунт",
                                                            f"Добро пожаловать, {login}, пожалуйста, введите ваш пароль:")
                if ok_pressed and password:
                    query = '''Select login From accounts where password = ?'''
                    data = self.cur.execute(query, (password,)).fetchall()
                    check = ''.join([str(i)[2:-3] for i in data])
                    if check == login:
                        self.mbox.setWindowTitle('Успех')
                        self.mbox.setText('Вы успешно вошли в свой аккаунт.')
                        self.mbox.exec()
                        query = f'''Select login, password, status From accounts where login = {str(data)[2:-3]}'''
                        account_turple = (self.cur.execute(query).fetchall())
                        self.account = [elem for elem in account_turple[0]]
                        self.AccountStr.setText(f'Добро пожаловать, {self.account[0]}')
                        self.check_status()
                    else:
                        self.mbox.setWindowTitle('Ошибка')
                        self.mbox.setText('Неправильный пароль.')
                        self.mbox.exec()
                elif ok_pressed and password == '':
                    self.mbox.setWindowTitle('Ошибка')
                    self.mbox.setText('Пожалуйста, введите ваш пароль.')
                    self.mbox.exec()
            else:
                self.mbox.setWindowTitle('Ошибка')
                self.mbox.setText('Неправильный логин.')
                self.mbox.exec()
        elif ok_pressed and login == '':
            self.mbox.setWindowTitle('Ошибка')
            self.mbox.setText('Пожалуйста, введите ваш логин.')
            self.mbox.exec()

    def check_status(self):
        if self.account[2] == 1:
            self.AdminPB.show()
        else:
            self.AdminPB.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())
