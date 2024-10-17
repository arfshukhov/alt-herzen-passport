import json
from typing import *

from backend.models import Institutes


class InstitutesReader:
    institute: Union[Institutes, None]
    """
    Данный класс реализует чтение из таблицы Institutes
    то по айди института
    образец использования: InstitutesReader(_id).get
    """
    def __init__(self,
                 _id: int):
        if _id:
            self.institute = Institutes.select().where(Institutes.id == _id).get()
        else:
            self.institute = None


    @property
    def get(self) -> Union[dict, None]:
        if not self.institute:
            return None
        return {"name":self.institute.name,
                "id":self.institute.id,
                }
    
class InstitutesList:
    """
    Возвращает список институтов по диапазону их ID
    Образец использования: InstitutesList(skip, limit).get
    """
    def __init__(self,
                 skip:int,
                 limit:int):
        self.skip = skip
        self.limit = limit
        self.institutes_list: List[Dict] = []

    def _make_list(self):
        """
        Если института с таким ID не сущесвтует,
        он просто не заносит его в список
        """
        for i in range(self.skip, self.limit+1):
            institute = InstitutesReader(_id=i).get
            if institute:
                self.institutes_list.append(institute)

    @property
    def get(self)->List[Dict]:
        self._make_list()
        return self.institutes_list