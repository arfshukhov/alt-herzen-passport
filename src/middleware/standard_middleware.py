from ..models  import *
from ..origin import *


class StandardReader:
    def __init__(self, *, student_id:Union[int, None]=None):
        self.source = {"standard":Standard, "result":StandardResults}
        if student_id:
            self.student_id = student_id
        else:
            self.student_id = None


    @property
    def get_standard(self):
        res: Dict = {"data": list(dict()), "count": 0}
        for i in session.query(self.source["standard"]).all():
            res["data"].append({
                "id":i.id,
                "name":i.name
            })
        res["count"] = len(res["data"])

        return res

    @property
    def get_res(self):
        if not self.student_id:
            raise ValueError("student_id cannot be None")
        q = session.query(self.source["result"]).filter_by(student_id=self.student_id).all()
        res: Dict[str, Union[List[Dict], int]] = {"data": [], "count": 0}
        for i in q:
            i_dict = i.__dict__
            i_dict.pop("_sa_instance_state")
            res["data"].append(i_dict)
        res["count"] = len(res["data"])
        return res


class StandardWriter:
    def __init__(self, *,
                 student_id:Union[int, None]=None,
                 standard_id:Union[int, None]=None,
                 result:Union[int, None]=None,
                 semester:Union[int, None]=None,
                 name:Union[int, None]=None,
                 result_id:Union[int, None]=None,):

        self.name=name
        self.student_id=student_id
        self.standard_id=standard_id
        self.result=result
        self.semester=semester
        self.result_id=result_id

    def write_result(self):
        for i in [self.student_id, self.standard_id, self.result, self.semester]:
            if not i:
                raise ValueError("student_id or standard_id or result or semester cannot be None")
        q = StandardResults(
            student_id=self.student_id,
            standard_id=self.standard_id,
            result=self.result,
            semester=self.semester,
        )
        session.add_all(q)
        session.commit()
        result = StandardReader(student_id=self.student_id).get_res
        for i in result["data"]:
            if i["standard_id"]==self.standard_id and i["semester"]==self.semester:
                return i
        else:
            raise NoResultFound("not found")

    def write_standard(self):
        if not self.name:
            raise ValueError("self.name cannot be None")
        q = Standard(name=self.name)
        session.add_all(q)
        session.commit()
        result = StandardReader(name=self.name).get_standard
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

