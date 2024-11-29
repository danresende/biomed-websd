import time

from flask_login import UserMixin

from app import login
from config import Config
from firebase import auth, db

admin = Config.ADMIN


class User(UserMixin):
    def __init__(self, localId, idToken, refreshToken):
        self.localId = localId
        self.idToken = idToken
        self.refreshToken = refreshToken

    def load_user_info(self):
        try:
            user = db.child("users").child(self.localId).get(self.idToken)
            user = {info.key(): info.val() for info in user.each()}
            self.nome = user["nome"]
            self.sobrenome = user["sobrenome"]
            self.email = user["email"]
            self.departamento = user["departamento"]
            self.DBA = bool(user["DBA"])
            self.RD = bool(user["RD"])
        except Exception as e:
            self.nome = "Cadatrar"
            self.sobrenome = "Usuário"
            self.email = admin
            self.departamento = "Sem departamento"
            self.DBA = False
            self.RD = False
            print(e)
        return None

    def reset_token(self):
        token = auth.refresh(self.refreshToken)["idToken"]
        self.idToken = token
        self.start_session(time.time())
        return None

    def start_session(self, time):
        self.startSession = time

    def session_over(self):
        return (time.time() - self.startSession) > 3000

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.localId, self.refreshToken


@login.user_loader
def load_user(user_info):
    user_id, user_refresh_token = user_info
    user_token = auth.refresh(user_refresh_token)["idToken"]
    user = User(user_id, user_token, user_refresh_token)
    user.start_session(time.time())
    user.load_user_info()
    return user
