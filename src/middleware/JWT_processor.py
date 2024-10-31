from functools import wraps
from typing import Union

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.sync import update
from werkzeug.exceptions import NotFound

from .users_middleware import UserReader
from ..origin import jwt, app, request, jsonify
from ..settings import ServerSettings
import datetime
from ..models import Users, session, Tokens
from .crypto import crypto
from .validator import Password


class PasswordManager:
    """
    Класс `PasswordManager` предназначен для управления паролями пользователей,
    включая обновление пароля и проверку соответствия пароля для авторизации.
    Методы:
    -------
    update_password(email: str, password: str):
        Обновляет пароль пользователя на новый хэш, если учетная запись с указанным email существует.
        Если пользователь не найден, вызывает исключение `NoResultFound`.
    match_password(email: str, password: str) -> bool:
        Проверяет, соответствует ли пароль указанному email. Возвращает 1, если авторизация успешна, и 0 - если нет.
    Исключения:
    -----------
    NoResultFound:
        Вызывается, если пользователь с указанным email не найден при обновлении пароля.
    """
    @classmethod
    def update_password(cls, email, password):
        """
        Обновляет пароль пользователя в базе данных.

        Параметры:
        ----------
        email : str
            Email пользователя, для которого нужно обновить пароль.
        password : str
            Новый пароль, который будет захэширован перед сохранением.

        Исключения:
        -----------
        NoResultFound:
            Вызывается, если пользователь с указанным email не найден в базе данных.
        """
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
        Сравнивает введенный пароль с сохраненным хэшем для авторизации.

        Параметры:
        ----------
        email : str
            Email пользователя.
        password : str
            Введенный пароль для проверки.

        Возвращает:
        ----------
        bool
            1, если введенный пароль соответствует сохраненному хэшу, и 0 - если не соответствует.
        """
        account = session.query(Users).filter(Users.email == email).one()
        password = Password(password).get
        #print(account.password_hash==password)
        if account.password_hash == password:
            return 1
        else:
            return 0


class Token:
    """
    Класс `Token` предназначен для создания, проверки и управления токенами доступа.
    Реализует создание токена для указанного email, деактивацию токена и валидацию токенов.

    Атрибуты:
    ----------
    email : str
        Email пользователя, связанный с токеном.

    Методы:
    -------
    deactivate():
        Деактивирует текущий токен в базе данных.

    make(email: str) -> str:
        Создает и сохраняет новый токен JWT для указанного email, сгенерированный с
        временной меткой истечения срока действия (по умолчанию — через 60 часов).

    get_token : str (property)
        Возвращает текущий токен.

    verify_token(token: str) -> dict:
        Проверяет токен JWT на действительность, возвращая информацию об email и статусе активности.

    token_required(func):
        Декоратор, проверяющий токен на действительность перед вызовом функции.

    Примеры:
    --------
    - Создание токена по email:
        >>> token = Token(email="user@example.com")
        >>> token.get_token

    - Проверка токена:
        >>> Token.verify_token(token=token.get_token)

    Исключения:
    -----------
    ValueError:
        Выбрасывается при некорректном токене в декораторе `token_required`.
    """
    email: str

    def __init__(self,
                 email: Union[str, None]=None,
                 token: Union[str, None]=None):
        """
        Инициализирует объект `Token` с токеном или email, создает новый токен, если указан email.

        Параметры:
        ----------
        email : str, optional
            Email пользователя, для которого создается новый токен.

        token : str, optional
            Существующий токен, который будет инициализирован в объекте.
        """
        if email:
            self.email = email
            self.token = self.make(self.email)
        elif token:
            self.token = token

    def __repr__(self):
        return self.token

    def __str__(self):
        return self.token

    def deactivate(self):
        """
        Деактивирует текущий токен в базе данных, устанавливая поле is_active в False.
        """
        q = session.query(Tokens).filter(token=self.token).update(is_active=False)
        session.commit()

    @property
    def get_token(self):
        """
        Возвращает токен.
        """
        return self.token

    def make(self, email):
        """
        Создает новый токен JWT для указанного email с временной меткой истечения.

        Параметры:
        ----------
        email : str
            Email, для которого создается токен.

        Возвращает:
        ----------
        str
            Сгенерированный токен JWT.
        """
        jwt_token = jwt.encode({
                "email": email,
                "expiration":str((datetime.datetime.now()+datetime.timedelta(seconds=60*60*60))
                                 .strftime("%Y-%m-%d %H:%M:%S"))
            },
                ServerSettings.SECRET_KEY, algorithm='HS256')
        q = Tokens(token=jwt_token, is_active=True)
        session.add(q)
        session.commit()
        return jwt_token

    @staticmethod
    def verify_token(token:str) -> dict:
        """
        Проверяет токен JWT на действительность.

        Параметры:
        ----------
        token : str
            JWT токен для проверки.

        Возвращает:
        ----------
        dict
            Словарь с данными email и статусом ("active"/"inactive").
        """
        data = jwt.decode(token, ServerSettings.SECRET_KEY, algorithms=['HS256'])
        if datetime.datetime.now() < datetime.datetime.strptime(data['expiration'],"%Y-%m-%d %H:%M:%S"):
            return {"email": data["email"], "status": "active"}
        else:
            return {"status": "inactive"}

    @staticmethod
    def token_required(func):
        """
         Декоратор, проверяющий токен перед вызовом функции.

         Если токен валиден и активен, функция выполняется с переданным email.
         В противном случае возвращает сообщение об ошибке авторизации.

         Параметры:
         ----------
         func : callable
             Функция, которую нужно вызвать, если токен валиден.

         Возвращает:
         ----------
         callable
             Функция-обертка, выполняющая проверку токена.
         """
        @wraps(func)
        def wrapper(*args, **kwargs):

            try:
                token = request.headers["Authorization"].split()[1]
                token_status = Token.verify_token(token)
                query_token = session.query(Tokens).filter_by(token=token).first()
                if token_status["status"] == "active" and query_token.is_active==True:
                    return func(_email=token_status["email"], *args, **kwargs)
                else:
                    return jsonify({"message": "unauthorized"}), 401
            except Exception as e:
                return jsonify({"message": "incorrect token", "reason": str(e)}), 422
        return wrapper