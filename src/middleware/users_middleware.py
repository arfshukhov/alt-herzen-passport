import json

from typing import *

from peewee import DoesNotExist, IntegrityError
from werkzeug.exceptions import NotFound

from ..middleware.validator import Email, FullName, Password, Id
from ..models import Users, session, NoResultFound


class UserReader:
    user: Union[str, None]
    """
    Данный класс реализует чтение из таблицы Users
    Если инициализировать объект класса по емейлу,
    то поиск в таблице будет осуществляться по емейлу;
    если по _id, то по айди пользователя
    """
    def __init__(self, *,
                 email: Union[str|None] = None,
                 _id: Union[int|None] = None
                 ):

        if email:
            self.user = session.query(Users).filter(Users.email == email).one_or_none()
        elif _id:
            self.user = session.query(Users).filter(Users.id == _id).one_or_none()
        else:
            self.user = None


    @property
    def get(self) -> Union[dict, None]:
        if not self.user:
            return None
        return {"email":self.user.email,
                "id":self.user.id,
                "is_active":self.user.is_active,
                "is_superuser":self.user.is_superuser,
                "full_name":self.user.full_name
                }


class UserWriter:
    _id: Union[int, None]
    email: Union[str, None]
    full_name: Union[str, None]
    def __init__(self, *, email:Union[str|None] = None,
                 is_active: bool = True,
                 is_superuser: bool = False,
                 full_name: Union[str, None] = None,
                 password: Union[str, None] = None,
                 _id=0):
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
        user = Users(
            email=self.data["email"],
            is_active=self.data["is_active"],
            is_superuser=self.data["is_superuser"],
            full_name=self.data["full_name"],
            password_hash=self.data["password"]
        )

        # Добавляем пользователя в сессию и фиксируем изменения
        session.add(user)
        session.commit()
        return {
            "email":self.data["email"],
            "is_active":bool(self.data["is_active"]),
            "is_superuser":bool(self.data["is_superuser"]),
            "full_name":self.data["full_name"],
            "id":UserReader(email=self.data["email"]).get["id"]}

    def update(self):
        result = session.query(Users).filter(Users.email == self.email).update({
            "email": self.email,
            "full_name": self.full_name,
        })

        session.commit()

        if result == 0:
            raise NoResultFound("User does not exist")

    def update_by_id(self):
        # Выполняем обновление
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
        session.commit()

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


