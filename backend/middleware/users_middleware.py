import json
from typing import *

from peewee import DoesNotExist, IntegrityError
from werkzeug.exceptions import NotFound

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
                 password: str,
                 _id=0):
        self.id = _id
        self.error: list = []
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
        ).save()
        return {
            "email":self.data["email"],
            "is_active":bool(self.data["is_active"]),
            "is_superuser":bool(self.data["is_superuser"]),
            "full_name":self.data["full_name"],
            "id":UserReader(email=self.data["email"]).get["id"]}

    @classmethod
    def update(self, email: str, full_name: str):
        upd = Users.update({
            Users.email: email,
            Users.full_name: full_name,
        }).where(Users.email == email).execute()
        if upd == 0:
            raise DoesNotExist("User does not exist")

    def update_by_id(self):
        ups = Users.update({
            Users.full_name: self.data["full_name"],
            Users.email: self.data["email"],
            Users.is_active: self.data["is_active"],
            Users.is_superuser: self.data["is_superuser"],
            Users.password_hash: self.data["password"]
        }).where(Users.id == self.id).execute()
        if ups == 0:
            raise DoesNotExist("User does not exist")

    @classmethod
    def delete_by_id(cls, _id, email):
        usr = UserReader(_id=_id).get
        if usr["email"] != email:
            raise ValueError("difference between arg email and user's email")
        else:
            del_ = Users.delete().where(Users.id == _id).execute()
            if del_ == 0:
                raise DoesNotExist("User does not exist")



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
        self.count = Users.select().count()
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
            except DoesNotExist:
                break

    @property
    def get(self)->List[Dict]:
        self._make_list()
        return self.users_list[self.skip: self.skip+self.limit]


