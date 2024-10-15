from typing import Any

from models import Users
from origin import *

class UserReader:
    """
    Данный класс реализует чтение из таблицы Users
    Если инициализировать объект класса по емейлу,
    то поиск в таблице будет осуществляться по емейлу;
    если по _id, то по айди пользователя
    """
    def __init__(self, *,
                 email: str|None = None,
                 _id: int|None = None):
        if email:
            self.user = Users.select().where(Users.email == email)
        if _id:
            self.user = Users.select().where(Users.id == _id)

    def __repr__(self) -> dict[str, Any[int,str]]:
        return {"email":self.user.email,
                "id":self.user.id,
                "is_active":self.user.is_active,
                "is_superuser":self.user.is_superuser,
                "full_name":self.user.full_name
                }

class UserWriter:
    def __init__(self,):...


