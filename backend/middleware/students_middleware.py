from typing import Union

from .groups_middleware import GroupsReader
from .institute_middleware import InstitutesReader
from ..models import Students, Groups


class StudentsReader:
    def __init__(self, _id=int):
        self._id = _id
        self.student = Students.select().where(Students.id == _id).get()
        self.group = GroupsReader(self.student.group_id).get
        self.institute = InstitutesReader(self.group["institute_id"]).get

    @property
    def get(self)-> Union[dict, None]:
        if self.student:
            return {
                "first_name": self.student.first_name,
                "last_name": self.student.last_name,
                "patronymic": self.student.patronymic,
                "birth_date": self.student.birth_date,
                "sex": self.student.sex,
                "medical_group": self.student.medical_group,
                "height": self.student.height,
                "weight": self.student.weight,
                "email": self.student.email,
                "phone": self.student.phone,
                "admission_year": self.student.admission_year,
                "birth_place": self.student.birth_place,
                "adress": self.student.adress,
                "id":self.student.id,
                "group_id":self.group["id"],
                "group":{
                    "name":self.group["name"],
                    "course":self.group["course"],
                    "id":self.group["id"],
                    "institute_id":self.institute["id"],
                    "institute":{
                        "name":self.institute["name"],
                        "id":self.institute["id"],
                    }
                }
            }

class StudentsList:
    def __init__(self, *,
                 institute_id: Union[int, None]=None,
                 group_id: Union[int, str]=None):
        if institute_id:
            self.institute_id
