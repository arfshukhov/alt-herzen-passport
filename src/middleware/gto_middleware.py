
from werkzeug.exceptions import NotFound

from src.middleware.institute_middleware import InstitutesReader
from .groups_middleware import GroupsList
from .students_middleware import StudentsReader
from .validator import LevelGTO
from ..origin import *
from ..models import *

class GTOReader:
    """
    Данный класс предназначен для работы с данными
    по результатам ГТО.
    """
    def __init__(self, *,
                 institute_id:Union[int, None] = None,
                 group_id:Union[int, None] = None,
                 student_id:Union[int, None] = None):
        self.institute_id = institute_id
        self.group_id = group_id
        self.student_id = student_id
        self.institute = InstitutesReader(self.institute_id).get
        self.groups: List[Dict] = []
        self.students: List[Dict] = []
        self.gto_results: Dict[str, int] = {"gold":0, "silver":0, "bronze":0}


    def compare_groups(self):
        """
        Метод создает список из словарей с информацией
        о группах, принадлежащих институту, указанному в
        institute_id
        """
        #count = Groups.select().count()
        count = session.query(Groups).count()
        #print("count=",count)
        for i in range(1, 7):
            self.groups.extend(
                GroupsList(institute_id=self.institute_id,
                           course=i, skip=1,limit=count
                           ).get
            )
        #print("groups=",self.groups)

    def compare_students(self):
        """
        пользуясь результатами метода compare_groups(),
        этот метод создает список из словарей с данными студентов,
        которые состоят в группах, которые принадлежат указанному в
        institute_id институту.
        Если указать group_id, то данный метод сформирует список из студентов,
        состоящих в группах с id=group_id
        """
        #count = Students.select().count()
        count = session.query(Students).count()
        #print(self.groups)
        for i in range(1,count+1):
            student = StudentsReader(_id=i).get
            #print("student=",student)
            if student:
                #print("is stud")
                if self.group_id:
                    if student["group_id"] == self.group_id:
                        self.students.append(student)
                else:
                    for k in self.groups:
                        if student["group_id"] == int(k["id"]):
                            self.students.append(student)

    def compare_results(self):
        if self.student_id:
            res = session.query(BaseGTO).filter(
                (BaseGTO.student_id == self.student_id) &
                (BaseGTO.year == datetime.now().year)
            ).one_or_none()
            self.gto_results[res.level] += 1
        for i in self.students:
            res = session.query(BaseGTO).filter(
                (BaseGTO.student_id == i['id']) &
                (BaseGTO.year == datetime.now().year)
            ).one_or_none()
            self.gto_results[res.level] += 1

    @property
    def get_by_one_institute(self):
        self.compare_groups()
        self.compare_students()
        self.compare_results()
        return self.gto_results

    @property
    def get_by_group(self):
        self.compare_students()
        self.compare_results()
        return self.gto_results

    @property
    def get_by_student(self):
        self.compare_results()
        return self.gto_results

    @property
    def get_all_members(self):
        gold = session.query(BaseGTO).filter(
            BaseGTO.level == "gold"
        ).count()
        silver = session.query(BaseGTO).filter(
            BaseGTO.level == "silver"
        ).count()
        bronze = session.query(BaseGTO).filter(
            BaseGTO.level == "bronze"
        ).count()
        return {
            "gold": gold,
            "silver": silver,
            "bronze": bronze
        }

class RatingByInstitute:
    def __init__(self, *,
                 institute_id:int):
        self.institute_id = institute_id
        self.positions: Dict[int,Dict[str,int]] = {} #institute_id: {level: count}
        self.count = session.query(Institutes).count()
        self.rating: Dict[str,List[Dict[int,int]]] = {
            "gold":[],
            "silver":[],
            "bronze":[]
        }
        self.institute_rating = {}
        # level: [{institute_id: institute_rating}]

    def compare_positions(self):
        for i in range(1,self.count+1):
            self.positions[i] = GTOReader(institute_id=i).get_by_one_institute

    def compare_rating(self):
        gold: List[Dict[int, int]] = []
        silver: List[Dict[int, int]] = []
        bronze: List[Dict[int, int]] = []
        for institute_id, data in self.positions.items():
            for level, _count in self.positions[institute_id].items():
                match level:
                    case "gold":
                        gold.append({
                            institute_id: self.positions[institute_id]["gold"]
                        })
                    case "silver":
                        silver.append({
                            institute_id: self.positions[institute_id]["silver"]
                        })
                    case "bronze":
                        bronze.append({
                            institute_id: self.positions[institute_id]["bronze"]
                        })
        gold.sort(key=lambda x: int(*x.values()), reverse=True)
        silver.sort(key=lambda x: int(*x.values()), reverse=True)
        bronze.sort(key=lambda x: int(*x.values()), reverse=True)
        for place, elem in enumerate(gold, start=1):
            for institute_id, count_res in elem.items():
                if institute_id == self.institute_id:
                    self.institute_rating["gold"] = place
        for place, elem in enumerate(silver, start=1):
            for institute_id, count_res in elem.items():
                if institute_id == self.institute_id:
                    self.institute_rating["silver"] = place
        for place, elem in enumerate(bronze, start=1):
            for institute_id, count_res in elem.items():
                if institute_id == self.institute_id:
                    self.institute_rating["bronze"] = place

    @property
    def get(self):
        self.compare_positions()
        self.compare_rating()
        return self.institute_rating


class AssemblerGTO:
    def __init__(self, *,institute_id:int):
        self.institute_id = institute_id
        self.gto_results: Dict[str, int] = GTOReader(
            institute_id=self.institute_id,
        ).get_by_one_institute
        self.rating = RatingByInstitute(institute_id=institute_id).get
        self.all_members = GTOReader(
            institute_id=self.institute_id,
        ).get_all_members
        self.data = {
            "count_by_institute": {
                "gold": self.gto_results["gold"],
                "silver": self.gto_results["silver"],
                "bronze": self.gto_results["bronze"]
            },
            "members_count":{
                "gold":self.all_members["gold"],
                "silver":self.all_members["silver"],
                "bronze":self.all_members["bronze"]
            },
            "rating":{
                "gold":self.rating["gold"],
                "silver":self.rating["silver"],
                "bronze":self.rating["bronze"]
            },
            "percent_by_common":{
                "gold":0 ,
                "silver":0,
                "bronze":0
            }
        }

    @property
    def get(self):
        if self.gto_results["gold"]+self.gto_results["silver"]+self.gto_results["bronze"]!=0:
            for i in ["gold","silver","bronze"]:
                self.data["percent_by_common"][i] = self.gto_results[i]/(
                    self.gto_results["gold"]+self.gto_results["silver"]+self.gto_results["bronze"]
                )*100
        return self.data

class GTOWriter:
    def __init__(self, *,
                 student_id: int,
                 level: str
                 ):
        self.student_id = student_id
        self.level = LevelGTO(level).get

    def write(self):
        gto = BaseGTO(
            student_id=self.student_id,
            level=self.level,
            year=datetime.now().year
        )
        session.add(gto)  # Добавляем объект в сессию
        session.commit()  # Сохраняем изменения в базе данных

        return {"student_id":self.student_id, "level":self.level}

    def update(self):
        # Находим запись для обновления
        gto = session.query(BaseGTO).filter(
            (BaseGTO.student_id == self.student_id) &
            (BaseGTO.year == int(datetime.now().year))
        ).one_or_none()

        if gto:
            gto.level = self.level  # Обновляем уровень
            session.commit()  # Сохраняем изменения
            return {"student_id": self.student_id, "level": self.level}
        else:
            raise NoResultFound(f"{self.student_id} not found.")



