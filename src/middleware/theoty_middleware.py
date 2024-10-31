from typing import Union, Dict

from .standard_middleware import StandardReader
from ..models import (
    Theory, TheoryResults, NoResultFound, session
)

class TheoryReader(StandardReader):
    def __init__(self, *,
                 student_id:Union[int, None]=None):
        self.source = {"standard":Theory, "result":TheoryResults}
        self.student_id = student_id


class TheoryWriter:
    def __init__(self, *,
                 student_id:Union[int, None]=None,
                 theory_id:Union[int, None]=None,
                 result:Union[int, None]=None,
                 semester:Union[int, None]=None,
                 name:Union[int, None]=None,
                 result_id:Union[int, None]=None,):

        self.name=name
        self.student_id=student_id
        self.theory_id=theory_id
        self.result=result
        self.semester=semester
        self.result_id=result_id

    def write_result(self):
        for i in [self.student_id, self.theory_id, self.result, self.semester]:
            if not i:
                raise ValueError("student_id or theory_id or result or semester cannot be None")
        q = TheoryResults(
            student_id=self.student_id,
            theory_id=self.theory_id,
            result=self.result,
            semester=self.semester,
        )
        session.add_all(q)
        session.commit()
        result = StandardReader(student_id=self.student_id).get_res
        for i in result["data"]:
            if i["theory_id"]==self.theory_id and i["semester"]==self.semester:
                return i
        else:
            raise NoResultFound("not found")

    def write_standard(self):
        if not self.name:
            raise ValueError("self.name cannot be None")
        q = Theory(name=self.name)
        session.add_all(q)
        session.commit()
        result = TheoryReader(name=self.name).get_standard
        for i in result["data"]:
            if i["name"]==self.name:
                return i
        else:
            raise NoResultFound("standard not found")

    def update_result(self):
        if not self.result_id or not self.student_id:
            raise ValueError("self.student_id and self.result_id cannot be None")

        # Attempt to update the record directly
        q = session.query(StandardResults).filter(
            StandardResults.student_id == self.student_id,
            StandardResults.id == self.result_id
        )

        # Check if the record exists and update
        if q.update({"result":self.result   }) == 0:
            raise NoResultFound("student_id or result_id is incorrect")

        # Commit the session after updates
        session.commit()

        # Fetch updated result to confirm changes
        res = StandardReader(student_id=self.student_id).get_res
        for i in res["data"]:
            if i["id"] == self.result_id:
                return i
        else:
            raise NoResultFound("The result was not found after update")

    def delete_result(self):
        if not self.result_id:
            raise ValueError("self.result_id cannot be None")
        q = session.query(StandardResults).filter(StandardResults.id==self.result_id).delete()
        session.commit()