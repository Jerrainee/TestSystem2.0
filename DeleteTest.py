from PyQt5.QtWidgets import QMainWindow, QInputDialog, QMessageBox


class DeleteTest(QMainWindow):
    def __init__(self, con, cur, RowsLst):
        super().__init__()
        self.con = con
        self.cur = cur
        self.RowsLst = RowsLst
        self.initUI()

    def initUI(self):
        self.mbox = QMessageBox(self)
        self.flag = True
        self.delete_test()

    def delete_test(self):
        ID, ok_pressed = QInputDialog.getText(self, "Удаление",
                                              "Пожалуйста, введите Id теста:")
        if ok_pressed and ID:
            for row in self.RowsLst:
                if row[0] == int(ID) and self.flag:
                    name, subject = row[1], row[2]
                    valid = QMessageBox.question(
                        self, '', f"Действительно удалить данный тест: {name} по предмету {subject}? ",
                        QMessageBox.Yes, QMessageBox.No)
                    if valid == QMessageBox.Yes:
                        query = "DELETE FROM Tests WHERE Id= ?"
                        self.cur.execute(query, (ID,)).fetchall()
                        self.con.commit()
                        self.flag = False
                else:
                    if row[0] == self.RowsLst[-1][0] and self.flag:
                        self.mbox.setWindowTitle('Ошибка')
                        self.mbox.setText('Тест с данным Id не найден')
                        self.mbox.exec()
                        self.flag = False
        else:
            if ID == '' and ok_pressed:
                self.mbox.setWindowTitle('Ошибка')
                self.mbox.setText('Пожалуйста, введите Id теста')
                self.mbox.exec()
