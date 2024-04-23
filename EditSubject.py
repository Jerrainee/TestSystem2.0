from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox


class EditSubject(QMainWindow):
    def __init__(self, con, cur):
        super().__init__()
        self.con = con
        self.cur = cur
        self.initUI()

    def initUI(self):
        self.mbox = QMessageBox(self)
        self.choice_act()

    def choice_act(self):
        request, ok_pressed = QInputDialog.getItem(
            self, 'Меню', 'Выберите дейсвие:',
            ('Добавить предмет', 'Удалить предмет'), 0, False)
        if ok_pressed:
            if request == 'Добавить предмет':
                self.add_subject()
            if request == 'Удалить предмет':
                self.delete_subject()

    def add_subject(self):
        subject, ok_pressed = QInputDialog.getText(self, "Название",
                                                   "Введите название предмета:")
        if ok_pressed and subject:
            valid = QMessageBox.question(
                self, '', f"Вы действительно хотите добавить данный предмет: {subject}?",
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                query = """ Insert into Subjects(Subject) Values(?) """
                self.cur.execute(query, (subject,)).fetchall()
                self.mbox.setWindowTitle('Успешно')
                self.mbox.setText('Предмет был успешно добавлен')
                self.mbox.exec()
                self.con.commit()
                self.close()
        elif ok_pressed and subject == '':
            self.mbox.setWindowTitle('Ошибка')
            self.mbox.setText('Пожалуйста, введите название предмета')
            self.mbox.exec()

    def delete_subject(self):
        query_sub = """ select Subject from Subjects """
        res = self.cur.execute(query_sub).fetchall()
        data_sub = [str(list(elem))[2:-2] for elem in res]

        subject, ok_pressed = QInputDialog.getItem(
            self, 'Меню', 'Выберите предмет, который желаете удалить:',
            (list(data_sub)), 0, False)
        if ok_pressed:
            dct = dict()
            query = f""" Select Id, Name From Tests
                         left join Subjects 
                         on Tests.Subject_ID = Subjects.Subject_ID
                         where subject = '{subject}'"""
            res = self.cur.execute(query).fetchall()
            valid = QMessageBox.question(
                self, '', f"Действительно удалить данный предмет: {subject}? ",
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                if res:
                    data = [str(list(elem)) for elem in res]
                    query_id = """ select Subject_ID from Subjects """
                    res = self.cur.execute(query_id).fetchall()
                    data_id = [str(list(elem))[1:-1] for elem in res]
                    for i in range(len(data_sub)):
                        dct[data_sub[i]] = data_id[i]
                    res_data = f'\n'
                    for elem in data:
                        res_data += f'{str(elem)[1:-1]}\n'
                    valid = QMessageBox.question(
                        self, 'Внимание',
                        f"Обратите внимание: Данные тесты(Id, имя) удалятся. Хотите продолжить? {res_data}",
                        QMessageBox.Yes, QMessageBox.No)
                    if valid == QMessageBox.Yes:
                        query = """ DELETE FROM Tests WHERE Subject_ID = ? """
                        self.cur.execute(query, (dct[subject],)).fetchall()
                query = """ DELETE FROM Subjects WHERE Subject = ? """
                self.cur.execute(query, (subject,)).fetchall()
                self.mbox.setWindowTitle('Успех')
                self.mbox.setText('Предмет успешно удален')
                self.mbox.exec()
                self.con.commit()
