import json
from typing import *

from backend.middleware.validator import Email, FullName, Password
from backend.models import Users


class UserReader:
    """
    Данный класс реализует чтение из таблицы Users
    Если инициализировать объект класса по емейлу,
    то поиск в таблице будет осуществляться по емейлу;
    если по _id, то по айди пользователя
    """
    def __init__(self, *,
                 email: Union[str|None] = None,
                 _id: Union[int|None] = None):
        if email:
            self.user = Users.select().where(Users.email == email).first().get()
        if _id:
            self.user = Users.select().where(Users.id == _id).first().get()

    @property
    def get(self) -> str:
        return json.dumps({"email":self.user.email,
                "id":self.user.id,
                "is_active":self.user.is_active,
                "is_superuser":self.user.is_superuser,
                "full_name":self.user.full_name
                })

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

    def __repr__(self):
        if len(self.error) > 0:
            return json.dumps(
                [{"detail": self.error}, 422]
            ),
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
                return json.dumps([0, 409])
            return json.dumps([{
                "email":self.data["email"],
                "is_active":bool(self.data["is_active"]),
                "is_superuser":bool(self.data["is_superuser"]),
                "full_name":self.data["full_name"],
                "id":int(Users.select().where(Users.email == self.data["email"]).first().id) }, 200]
            )





