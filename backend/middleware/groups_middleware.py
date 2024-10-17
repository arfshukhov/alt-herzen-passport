from typing import Union, Dict

from backend.models import Groups


class GroupsReader:
    def __init__(self, _id:int):
        self._id = _id

        self.group = Groups.select().where(Groups.id == _id).get()

    @property
    def get(self) -> Union[Dict, None]:
        if self.group:
            return {
                "id": self._id,
                "name": self.group.name,
                "course": self.group.course,
                "institute_id": self.group.institute_id,
            }
        return None
