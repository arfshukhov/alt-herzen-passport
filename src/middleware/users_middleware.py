import json

from typing import *

from werkzeug.exceptions import NotFound

from ..middleware.validator import Email, FullName, Password, Id
from ..models import Users, session, NoResultFound


class UserReader:
    """
    Класс `UserReader` предназначен для чтения данных из таблицы пользователей (Users).
    Этот класс позволяет искать пользователя по его email или идентификатору (ID).
    При инициализации экземпляра класса можно указать либо email, либо ID пользователя.

    Параметры:
    ----------
    email : str, optional
        Email пользователя, по которому будет выполнен поиск. Если указан,
        будет выполнен запрос к базе данных на наличие пользователя с данным email.

    _id : int, optional
        Идентификатор пользователя, по которому будет выполнен поиск.
        Если указан, будет выполнен запрос к базе данных на наличие пользователя с данным ID.

    Методы:
    -------
    get
        Возвращает словарь с данными пользователя или None, если пользователь не найден.

    Примеры:
    --------
    >>> user_reader = UserReader(email="user@example.com")
    >>> user_data = user_reader.get
    >>> print(user_data)  # {'email': 'user@example.com', 'id': 1, ...}
    """
    user: Union[str, None]
    def __init__(self, *,
                 email: Union[str|None] = None,
                 _id: Union[int|None] = None
                 ):
        """
        Инициализирует экземпляр класса `UserReader` с указанными параметрами `email` или `_id`
        Параметры:
        ----------
        email : str, optional
            Email пользователя для поиска
        _id : int, optional
            Идентификатор пользователя для поиска.
        """
        if email:
            self.user = session.query(Users).filter(Users.email == email).one_or_none()
        elif _id:
            self.user = session.query(Users).filter(Users.id == _id).one_or_none()
        else:
            self.user = None


    @property
    def get(self) -> Union[dict, None]:
        """
        Возвращает словарь с данными пользователя, если пользователь найден;
        в противном случае возвращает None
        Возвращает:
        ----------
        dict, optional
            Словарь с данными пользователя (email, id, is_active, is_superuser, full_name) или None.
        """
        if not self.user:
            return None
        return {"email":self.user.email,
                "id":self.user.id,
                "is_active":self.user.is_active,
                "is_superuser":self.user.is_superuser,
                "full_name":self.user.full_name
                }


class UserWriter:
    """
    Класс `UserWriter` предназначен для создания и обновления данных пользователей в таблице Users.
    Этот класс позволяет добавлять новых пользователей и изменять существующие записи по email или ID.

    Параметры:
    ----------
    email : str, optional
        Email пользователя. Должен быть уникальным.

    is_active : bool, default=True
        Статус активности пользователя. Если True, пользователь активен.

    is_superuser : bool, default=False
        Статус суперпользователя. Если True, пользователь имеет расширенные права.

    full_name : str, optional
        Полное имя пользователя.

    password : str, optional
        Пароль пользователя. Будет хэширован перед сохранением в базе данных.

    _id : int, default=0
        Идентификатор пользователя. Используется для обновления существующих пользователей.

    Методы:
    -------
    write
        Создает нового пользователя и добавляет его в базу данных.

    update
        Обновляет данные существующего пользователя по его email.

    update_by_id
        Обновляет данные существующего пользователя по его идентификатору (ID).

    Примеры:
    --------
    >>> user_writer = UserWriter(email="user@example.com", full_name="John Doe", password="securepassword")
    >>> new_user = user_writer.write()
    >>> print(new_user)  # {'email': 'user@example.com', ...}
    """

    _id: Union[int, None]
    email: Union[str, None]
    full_name: Union[str, None]
    def __init__(self, *, email:Union[str|None] = None,
                 is_active: bool = True,
                 is_superuser: bool = False,
                 full_name: Union[str, None] = None,
                 password: Union[str, None] = None,
                 _id=0):
        """
        Инициализирует экземпляр класса `UserWriter` с указанными параметрами.

        Параметры:
        ----------
        email : str, optional
            Email пользователя для создания или обновления.

        is_active : bool, default=True
            Статус активности пользователя.

        is_superuser : bool, default=False
            Статус суперпользователя.

        full_name : str, optional
            Полное имя пользователя.

        password : str, optional
            Пароль пользователя.

        _id : int, default=0
            Идентификатор пользователя для обновления.
        """
        if _id:
            self.id = Id(_id).get
        if email:
            self.email = Email(email).get
        if full_name:
            self.full_name = FullName(full_name).get
        self.error: list = []
        self.email = email
        self.data = {
            "email":Email(email).get,
            "is_active":is_active,
            "is_superuser":is_superuser,
            "full_name":FullName(full_name).get,
            "password":Password(password).get
        }

    def write(self)->Dict:
        """
        Создает нового пользователя и сохраняет его в базе данных.

        Возвращает:
        ----------
        dict
            Словарь с данными нового пользователя (email, is_active, is_superuser, full_name, id).

        Исключения:
        -----------
        ValueError
            Если пользователь с таким email уже существует.
        """
        user = Users(
            email=self.data["email"],
            is_active=self.data["is_active"],
            is_superuser=self.data["is_superuser"],
            full_name=self.data["full_name"],
            password_hash=self.data["password"]
        )

        # Добавляем пользователя в сессию и фиксируем изменения
        try:
            session.add(user)
            session.commit()
        except Exception:
            session.rollback()
            raise ValueError("User already exists")
        return {
            "email":self.data["email"],
            "is_active":bool(self.data["is_active"]),
            "is_superuser":bool(self.data["is_superuser"]),
            "full_name":self.data["full_name"],
            "id":UserReader(email=self.data["email"]).get["id"]}

    def update(self):
        """
        Обновляет данные существующего пользователя по его email.

        Исключения:
        -----------
        ValueError
            Если email уже зарегистрирован.
        NoResultFound
            Если пользователь не существует.
        """
        result = session.query(Users).filter(Users.email == self.email).update({
            "email": self.email,
            "full_name": self.full_name,
        })
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise ValueError("Email already registered")
        if result == 0:
            raise NoResultFound("User does not exist")

    def update_by_id(self):
        """
        Обновляет данные существующего пользователя по его идентификатору (ID).

        Исключения:
        -----------
        NoResultFound
            Если пользователь не существует.
        """
        result = session.query(Users).filter(Users.id == self.id).update({
            "full_name": self.data["full_name"],
            "email": self.data["email"],
            "is_active": self.data["is_active"],
            "is_superuser": self.data["is_superuser"],
            "password_hash": self.data["password"]
        })

        # Сохраняем изменения в базе данных
        session.commit()

        if result == 0:
            raise NoResultFound("User does not exist")

    def delete_by_id(self):
        usr = UserReader(_id=self._id).get  # Получаем пользователя

        if usr["email"] != self.email:
            raise ValueError("Difference between arg email and user's email")

        # Удаляем пользователя
        result = session.query(Users).filter(Users.id == self._id).delete()
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise ValueError("User does not exist")
        if result == 0:
            raise NoResultFound("User does not exist")



class UsersList:
    """
    Возвращает список пользователей по диапазону их ID
    Образец использования: UsersList(skip=skip, limit=limit).get
    или UsersList(institute_id=institute_id).get
    """
    def __init__(self,*,
                 skip:Union[int, None],
                 limit:Union[int,None],
                 ):
        self.skip = skip
        self.limit = limit
        self.count = session.query(Users).count()
        self.users_list: List[Dict] = []

    def _make_list(self):
        """
        Если пользователя с таким ID не сущесвтует,
        он просто не заносит его в список
        """
        for i in range(1, self.count + 1):
            try:
                user = UserReader(_id=i).get
                if user:
                    self.users_list.append(user)
            except NoResultFound:
                break

    @property
    def get(self)->List[Dict]:
        self._make_list()
        return self.users_list[self.skip: self.skip+self.limit]


