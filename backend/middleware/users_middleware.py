import json
from typing import *

from peewee import DoesNotExist

from ..middleware.validator import Email, FullName, Password
from ..models import Users


class UserReader:
    user: Union[Users, None]
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
            self.user = Users.select().where(Users.email == email).get()
        elif _id:
            self.user = Users.select().where(Users.id == _id).get()
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

    def __init__(self, *, email:str,
                 is_active: bool = True,
                 is_superuser: bool = False,
                 full_name: str,
                 password: str):
        self.error: list = []
        self.data = {
            "email":Email(email).get,
            "is_active":is_active,
            "is_superuser":is_superuser,
            "full_name":FullName(full_name).get,
            "password":Password(password).get
        }

        for key, value in self.data.items():
            if value == "invalid":
                self.error.append(
                    {"loc": [key, 0],
                     "msg":value,
                     "type": ""}
                )

    def write(self)->List:
        if len(self.error) > 0:
            return [{"detail": self.error}, 422]
            #),
        else:
            try:
                user = Users(
                    email=self.data["email"],
                    is_active=self.data["is_active"],
                    is_superuser=self.data["is_superuser"],
                    full_name=self.data["full_name"],
                    password_hash=self.data["password"]
                ).save()
            except Exception:
                return [0, 409]
            return [{
                "email":self.data["email"],
                "is_active":bool(self.data["is_active"]),
                "is_superuser":bool(self.data["is_superuser"]),
                "full_name":self.data["full_name"],
                "id":UserReader(email=self.data["email"]).get["id"]},
                200]



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

        self.users_list: List[Dict] = []

    def _make_list(self):
        """
        Если пользователя с таким ID не сущесвтует,
        он просто не заносит его в список
        """
        for i in range(self.skip, self.limit+1):
            user = UserReader(_id=i).get
            if user:
                self.users_list.append(user)

    @property
    def get(self)->List[Dict]:
        self._make_list()
        return self.users_list


