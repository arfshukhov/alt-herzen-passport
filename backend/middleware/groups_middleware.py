import logging
from typing import Union, Dict, List

from backend.middleware.institute_middleware import InstitutesReader
from backend.models import Groups, DoesNotExist


class GroupsReader:
    """
    Данный класс работает предназначе
    """
    def __init__(self, *, _id:int):
        self._id = _id
        try:
            self.group = Groups.select().where(Groups.id == self._id).get()
            self.institute = InstitutesReader(self.group.institute_id).get
        except DoesNotExist:
            self.group = None



    @property
    def get(self) -> Union[Dict, None]:
        if self.group:
            return {
                "id": self.group.id,
                "name": self.group.name,
                "course": self.group.course,
                "institute_id": self.institute["id"],
                "institute":
                    {
                    "name": self.institute["name"],
                    "id":self.institute["id"]
                    }
                }
        return None

class GroupsList:
    """
    класс реализует поиск групп по айди института
    и курса.
    пример использования:
    GroupsList(
                institute_id=1,
                course_id=1,
                skip=0,
                limit=100
    """
    def __init__(self,*,
                 institute_id: int,
                 course:int,
                 skip: int=0,
                 limit: int=100) :
        self.institute_id: int = institute_id
        self.course: int = course
        self.skip: int = skip
        self.limit: int = limit
        self.groups : List[Dict] = []
        self.count = Groups.select().count()

    def _make_list(self):
        for i in range(1, self.count+1):
            group = GroupsReader(_id=i).get
            if group:
                self.groups.append(group)
                #print(group)
        self.groups = list(
            filter(
                (lambda group: group["institute_id"] == self.institute_id and \
                    group["course"] == self.course), self.groups
            )
        )


    @property
    def get(self) -> List[Dict]:
        self._make_list()
        return self.groups[self.skip:self.skip+self.limit]
