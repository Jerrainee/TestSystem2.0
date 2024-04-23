from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox
import datetime

from Account import Account


class TestRun(QMainWindow):
    def __init__(self, con, cur, RowsLst, Id, Name, user):
        super().__init__()
        uic.loadUi('interface/TestRunInterface.ui', self)
        self.con = con
        self.cur = cur
        self.RowsLst = RowsLst
        self.user = user
        self.id = Id
        self.name = Name
        self.res_answers = []
        self.initUI()

    def initUI(self):
        self.Next.clicked.connect(self.next_question)
        self.Back.clicked.connect(self.previous_question)
        self.Save.clicked.connect(self.save_answer)
        self.QuestionNum = -1
        self.Flag = False
        self.mbox = QMessageBox(self)
        self.Flag2 = True
        self.current_test()

    def current_test(self):
        query = "Select * from Tests Where Id = ?"
        data = self.cur.execute(query, (self.id,)).fetchall()
        self.QuestLst = data[0][3].split(';;')
        self.AnswLst = data[0][4].split(';;')
        self.UserAnswers = dict.fromkeys([i for i in range(len(self.AnswLst))])
        self.next_question()

    def next_question(self):
        self.QuestionNum += 1
        if self.QuestionNum == len(self.QuestLst):
            self.QuestionNum -= 1
            self.Flag2 = False
            self.test_pass()
        if self.Flag2:
            self.check_buttons()
        self.textEdit.setText(self.QuestLst[self.QuestionNum])
        self.textEdit.isReadOnly()

    def previous_question(self):
        self.QuestionNum -= 1
        self.check_buttons()
        self.textEdit.setText(self.QuestLst[self.QuestionNum])
        self.textEdit.isReadOnly()

    def save_answer(self):
        self.UserAnswers[self.QuestionNum] = self.lineEdit.text()


    def check_buttons(self):
        self.label.setText(f'Вопрос №{self.QuestionNum + 1} :')
        if self.QuestionNum == 0:
            self.Back.hide()
        else:
            self.Back.show()
        if self.QuestionNum == len(self.QuestLst) - 1:
            self.Next.setText('Завершить')
        else:
            self.Next.setText('Далее')
        if self.UserAnswers[self.QuestionNum]:
            self.lineEdit.setText(self.UserAnswers[self.QuestionNum])
        else:
            self.lineEdit.setText('')

    def test_pass(self):
        valid = QMessageBox.question(
            self, '', 'Вы уверенны, что хотите завершить прохождение теста?',
            QMessageBox.Yes, QMessageBox.No)
        count = 0
        if valid == QMessageBox.Yes:
            self.close()
            for i, answ in enumerate(self.AnswLst):
                if self.UserAnswers[i]:
                    self.res_answers.append(self.UserAnswers[i])
                else:
                    self.res_answers.append('<None>')
                if self.UserAnswers[i] == answ:
                    count += 1
            result = f'{(count / len(self.AnswLst) * 100):.0f}'
            self.mbox.setWindowTitle('Успех')
            self.mbox.setText(
                f'Поздравляем, вы прошли тест на {count} / {len(self.AnswLst)}, {result}%')
            self.mbox.exec()
            if self.user:
                q = f''' Select Subject_ID from tests where ID == {self.id}'''
                cur_sub = self.cur.execute(q).fetchall()
                query = """ Insert into log(User_login, Test_id, Test_name, Test_subject_id, Result, User_answers, date) Values(?, ?, ?, ?, ?, ?, ?)"""
                print(self.res_answers)
                self.cur.execute(query,
                                 (self.user.login, self.id, self.name, cur_sub[0][0], result, ';;'.join(self.res_answers),
                                  datetime.datetime.now())).fetchall()
                self.con.commit()
