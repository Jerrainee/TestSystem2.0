from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox


class AddTest(QMainWindow):
    def __init__(self, con, cur):
        super().__init__()
        uic.loadUi('AddTestInterface.ui', self)
        self.con = con
        self.cur = cur
        self.initUI()

    def initUI(self):
        self.count = 0
        self.QuestLst = []
        self.AnswLst = []
        self.add.clicked.connect(self.add_question)
        self.save.clicked.connect(self.save_test)
        self.mbox = QMessageBox(self)

    def add_question(self):
        if str(self.question.toPlainText()) and str(self.answer.text()):
            self.QuestLst.append(str(self.question.toPlainText()))
            self.AnswLst.append(str(self.answer.text()))
            self.count += 1
            self.log1.setText(f'Вопрос успешно добавлен, текущее кол-во вопросов: {self.count}')
            self.question.setText('')
            self.answer.setText('')
        else:
            self.mbox.setWindowTitle('Ошибка')
            self.mbox.setText('Пожалуйста, заполните пустые поля')
            self.mbox.exec()

    def save_test(self):
        if self.QuestLst != [] and self.AnswLst != []:
            name, ok_pressed = QInputDialog.getText(self, "Название",
                                                    "Введите название теста:")
            if ok_pressed and name:
                dct = dict()
                query_sub = """ select Subject from Subjects """
                res = self.cur.execute(query_sub).fetchall()
                data_sub = [str(list(elem))[2:-2] for elem in res]
                query_id = """ select Subject_ID from Subjects """
                res = self.cur.execute(query_id).fetchall()
                data_id = [str(list(elem))[1:-1] for elem in res]
                for i in range(len(data_sub)):
                    dct[data_sub[i]] = data_id[i]

                subject, ok_pressed = QInputDialog.getItem(
                    self, 'Меню', 'Пожалуйста, выберите название предмета:',
                    (list(data_sub)), 0, False)

                if ok_pressed:
                    QStr = ';;'.join(self.QuestLst)
                    AStr = ';;'.join(self.AnswLst)
                    subject_id = dct[subject]
                    query = '''Insert into Tests(Name, Subject_ID, Questions, Answers) Values(?, ?, ?, ?)'''
                    self.cur.execute(query, (name, subject_id, QStr, AStr)).fetchall()
                    self.mbox.setWindowTitle('Успешно')
                    self.mbox.setText('Тест был успешно добавлен')
                    self.mbox.exec()
                    self.close()
                elif ok_pressed and subject == '':
                    self.mbox.setWindowTitle('Ошибка')
                    self.mbox.setText('Пожалуйста, введите название предмета')
                    self.mbox.exec()
            elif ok_pressed and name == '':
                self.mbox.setWindowTitle('Ошибка')
                self.mbox.setText('Пожалуйста, введите название теста')
                self.mbox.exec()
        else:
            self.mbox.setWindowTitle('Ошибка')
            self.mbox.setText('Пожалуйста, добавьте хотя бы один вопрос')
            self.mbox.exec()
        self.con.commit()
