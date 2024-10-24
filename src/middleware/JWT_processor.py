from base64 import b64decode
from functools import wraps

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.sync import update
from werkzeug.exceptions import NotFound

from .users_middleware import UserReader
from ..origin import jwt, app, request, jsonify
from ..settings import ServerSettings
import datetime
from ..models import Users, session
from .crypto import crypto
from .validator import Password


class PasswordManager:
    @classmethod
    def update_password(cls, email, password):
        upd = session.query(Users).filter_by(Users.email==email).update(
            {"password_hash":Password(password).get}
        )

        # Проверяем, была ли обновлена запись
        if upd == 0:
            raise NoResultFound("User not found to update password")

        # Выполняем обновление
        session.commit()

    @classmethod
    def match_password(cls, email, password) -> bool:
        """
        используется для сопоставления логина и пароля для авторизации
        :param email: строка
        :param password: строка
        :return: 1 или 0 в зависимости от успешности авторизации
        """
        account = session.query(Users).filter(Users.email == email).one()
        password = Password(password).get
        #print(account.password_hash==password)
        if account.password_hash == password:
            return 1
        else:
            return 0


class Token:
    email: str

    def __init__(self, email):
        self.email = email
        self.token = self.make(self.email)

    def __repr__(self):
        return self.token

    def __str__(self):
        return self.token

    @property
    def get_token(self):
        return self.token

    def make(self, email):
        jwt_token = jwt.encode({
                "email": email,
                "expiration":str((datetime.datetime.now()+datetime.timedelta(seconds=60*60*60))
                                 .strftime("%Y-%m-%d %H:%M:%S"))
            },
                ServerSettings.SECRET_KEY, algorithm='HS256')
        return jwt_token

    @staticmethod
    def verify_token(token:str) -> dict:
        data = jwt.decode(token, ServerSettings.SECRET_KEY, algorithms=['HS256'])
        #print(datetime.datetime.now(), data['expiration'])
        if datetime.datetime.now() < datetime.datetime.strptime(data['expiration'],"%Y-%m-%d %H:%M:%S"):
            return {"email": data["email"], "status": "active"}
        else:
            return {"status": "inactive"}

    @staticmethod
    def token_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                #print(request.headers)
                token_status = Token.verify_token(request.headers["Authorization"].split()[1])
                #print(token_status)
                if token_status["status"] == "active":
                    return func(_email=token_status["email"], *args, **kwargs)
                else:
                    return jsonify({"message": "unauthorized"}), 401
            except Exception as e:
                return jsonify({"message": "incorrect token", "reason": str(e)}), 422
        return wrapper