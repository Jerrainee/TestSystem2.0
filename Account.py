from werkzeug.security import generate_password_hash, check_password_hash


class Account():

    def __init__(self):
        self.id = ''
        self.login = ''
        self.hashed_password = ''
        self.is_admin = 0




    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def check_status(self):
        if self.account[2] == 1:
            return True
        return False