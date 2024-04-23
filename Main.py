import sys

import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QInputDialog, QMessageBox, QTableWidget
from werkzeug.security import generate_password_hash, check_password_hash

from AddTest import AddTest
from DeleteTest import DeleteTest
from EditSubject import EditSubject
from ProfileResults import ShowProfileResults
from ShowResults import ShowResults
from TestRun import TestRun
from Account import Account


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface/Main_Interface.ui', self)
        self.initUI()

    def initUI(self):
        self.mbox = QMessageBox(self)
        self.UpdatePB.clicked.connect(self.default_query)
        self.AdminPB.clicked.connect(self.for_admin)
        self.LoginPB.clicked.connect(self.log_in_account)
        self.RegisterPB.clicked.connect(self.reg_account)
        self.LogoutPB.clicked.connect(self.logout)
        self.ProfilePB.clicked.connect(self.profile)
        self.SortingCB.currentTextChanged.connect(self.sort_table)
        self.SearchPB.clicked.connect(self.search_test)
        self.tableWidget.itemDoubleClicked.connect(self.check_account)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.con = sqlite3.connect('db/TestSystemDB.db3')
        self.cur = self.con.cursor()
        self.RowsLst = []
        self.check_status()
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
        lst1 = ['Названию', 'Id', 'Предмету']
        lst2 = ['tests.Name', 'tests.ID', 'Subjects.Subject']
        column = str(lst2[lst1.index(self.SearchCB.currentText())])
        cur_query = self.query + f" where {column} like '%{text}%'"
        data = self.cur.execute(cur_query)
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
        if not user.login:
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
            self.dialog = TestRun(self.con, self.cur, self.RowsLst, Id, Name, user)
            self.dialog.show()

    def reg_account(self):
        login, ok_pressed = QInputDialog.getText(self, "Аккаунт",
                                                 "Пожалуйста, придумайте ваш логин:")

        query = '''Select login From accounts where login = ?'''
        data = self.cur.execute(query, (login,)).fetchall()

        if login and ok_pressed and not data:
            password, ok_pressed = QInputDialog.getText(self, "Аккаунт",
                                                        f"Добро пожаловать, {login}, пожалуйста, придумайте пароль:")
            if ok_pressed and len(password) >= 8:
                psw = generate_password_hash(password)

                query = '''Insert into Accounts(login, password, status) values(?, ?, ?)'''
                self.cur.execute(query, (login, psw, 0))
                self.con.commit()
                self.flash('Успех', 'Аккаунт зарегистрирован')
                user.login = login
                user.hashed_password = psw
                user.is_admin = 0
                self.check_status()

            else:
                self.flash('Ошибка', 'Пароль должен содержать 8 или более символов')
        else:
            self.flash('Ошибка', 'Такой логин уже существует')

    def log_in_account(self):
        login, ok_pressed = QInputDialog.getText(self, "Аккаунт",
                                                 "Пожалуйста, введите ваш логин:")

        query = '''Select * From accounts where login = ?'''
        data = self.cur.execute(query, (login,)).fetchall()

        if ok_pressed and login and data:

            password, ok_pressed = QInputDialog.getText(self, "Аккаунт",
                                                        f"Добро пожаловать, {login}, пожалуйста, введите ваш пароль:")

            if ok_pressed and check_password_hash(data[0][2], password):
                self.flash('Успех', 'Вы успешно вошли в аккаут')
                user.id = int(data[0][0])
                user.login = data[0][1]
                user.hashed_password = data[0][2]
                user.is_admin = data[0][3]
                self.check_status()
            else:
                self.flash('Ошибка', 'Неверный пароль!')
        else:
            self.flash('Ошибка', 'Пользователь с таким логином не найден!')

    def profile(self):
        self.dialog = ShowProfileResults(self.con, self.cur, user)
        self.dialog.show()

    def logout(self):
        user.id = ''
        user.login = ''
        user.hashed_password = ''
        user.is_admin = 0
        self.check_status()

    def check_status(self):
        if user.login:
            self.AccountStr.setText(f'Добро пожаловать, {user.login}')
            self.RegisterPB.hide()
            self.LoginPB.hide()
            self.ProfilePB.show()
            self.LogoutPB.show()
            if user.is_admin == 1:
                self.AdminPB.show()
        else:
            self.AccountStr.setText(f'Добро пожаловать, гость')
            self.RegisterPB.show()
            self.LoginPB.show()
            self.ProfilePB.hide()
            self.LogoutPB.hide()
            self.AdminPB.hide()

    def flash(self, title, content):
        self.mbox.setWindowTitle(title)
        self.mbox.setText(content)
        self.mbox.exec()


if __name__ == '__main__':
    user = Account()
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())
