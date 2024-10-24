from typing import Union
from unittest import case

from .validator import (
    Validator, FullName, Patronymic,
    Date, Sex, MedicalGroup, Height,
    Weight, Email, Phone, Year,
    BirthPlace, Address, Id
)
from ..origin import *

from peewee import DoesNotExist

from .groups_middleware import GroupsReader
#from .institute_middleware import InstitutesReader
from ..models import Students, Groups, session


class StudentsReader:
    """
    Данный класс считывает данные студентов и преобразует их
    в словарь. В качестве аргументов передаются:
    либо id студента, либо имя и id группы, в которой студент учится.
    Не следует передавать аргументы обоих вариантов, т.к. будет
    иметь место неопределенное поведение.
    """
    def __init__(self,*, _id:Union[int,None]=None,
                 name:Union[str,None]=None,
                 group_id:Union[int,None]=None,
                 email:Union[str,None]=None):
        self._id = _id
        self._name = name
        self._group_id = group_id
        if self._id:
            """
            Если указали айди в аргументах,
            то возвращаются данные по нему.
            """
            try:
                self.student = session.query(Students).filter(Students.id == _id).one()
                self.group = GroupsReader(_id=self.student.group_id).get
            except DoesNotExist:
                self.student = None
        elif self._name and self._group_id:
            """
            Если были указаны имя и айди группы, то мы возвращаем
            данные по ним
            """
            self.first_name, self.last_name = self._name.split()
            try:
                self.student = session.query(Students).filter(
                    (Students.first_name == self.first_name) &
                    (Students.last_name == self.last_name) &
                    (Students.group_id == self._group_id)
                ).one()
                self.group = GroupsReader(_id=self.student.group_id).get  # Важно добавить скобки для вызова метода
            except NoResultFound:
                self.student = None
        else:
            self.student = None

    @property
    def get(self)-> Union[Dict, None]:
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
                "phone_number": self.student.phone_number,
                "admission_year": self.student.admission_year,
                "birth_place": self.student.birth_place,
                "address": self.student.address,
                "id":self.student.id,
                "group_id":self.group["id"],
                "group": self.group
                }
        return None


class StudentsList:
    def __init__(self, *,
                 institute_id: Union[int, None]=None,
                 group_id: Union[int, str]=None,
                 name:Union[str,None]=None,
                 skip=0,
                 limit=100
                 ):

        self.students: Union[None, List[Dict]]
        self.count = session.query(Students).count()
        if institute_id:
            self.institute_id = institute_id
        elif group_id:
            self.group_id = group_id
        elif name:
            self.first_name, self.last_name = name.split()
            self.group_id = group_id
        else:
            self.students = None
        self.skip = skip
        self.limit = limit

    def _make_list(self):
        if self.institute_id:
            for i in range(1, self.count+1):
                student = StudentsReader(_id=i).get
                if student["institute_id"] == self.institute_id:
                    self.students.append(student)
        elif self.group_id:
            for i in range(1, self.count+1):
                student = StudentsReader(_id=i).get
                if student["group_id"] == self.group_id:
                    self.students.append(student)
        elif self.first_name and self.last_name:
            for i in range(1, self.count+1):
                student = StudentsReader(_id=i).get
                if student["first_name"] == self.first_name \
                    and student["last_name"] == self.last_name\
                        and student["group_id"] == self.group_id:
                    self.students.append(student)


    @property
    def get(self):
        self._make_list()
        if self.students:
            return list(set(self.students))[self.skip: self.skip+self.limit]


class StudentWriter:
    def __init__(self, *,
                 _id:int=0,
                 data: Dict[str, Union[int, str]] = {}
                 ):
        self._id = _id
        self.data = data
        self.data_to_update: Dict[str, Union[int, str]] = {}
        self.validate_data(self.data)

    def validate_data(self, data:Dict[str,Union[int,str]]):
        for key, value in data.items():
            match key:
                case "first_name":
                    self.data_to_update["first_name"] = FullName(value).get
                case "last_name":
                    self.data_to_update["last_name"] = FullName(value).get
                case "patronymic":
                    self.data_to_update["patronymic"] = Patronymic(value).get
                case "birth_date":
                    self.data_to_update["birth_date"] = Date(value).get
                case "sex":
                    self.data_to_update["sex"] = Sex(value).get
                case "medical_group":
                    self.data_to_update["medical_group"] = MedicalGroup(value).get
                case "height":
                    self.data_to_update["height"] = Height(value).get
                case "weight":
                    self.data_to_update["weight"] = Weight(value).get
                case "email":
                    self.data_to_update["email"] = Email(value).get
                case "phone_number":
                    self.data_to_update["phone_number"] = Phone(value).get
                case "admission_year":
                    self.data_to_update["admission_year"] = Year(value).get
                case "birth_place":
                    self.data_to_update["birth_place"] = BirthPlace(value).get
                case "address":
                    self.data_to_update["address"] = Address(value).get
                case "group_id":
                    self.data_to_update["group_id"] = Id(value).get
                case _:
                    raise ValueError("invalid data")

    def write(self):
        student = Students(**self.data_to_update)  # Создание экземпляра студента
        session.add(student)  # Добавляем объект в сессию
        session.commit()
        user = StudentsReader(
            name=f"{self.data_to_update["first_name"]} {self.data_to_update['last_name']}",
            group_id=self.data_to_update['group_id']
        ).get
        return user

    def update(self):
        result = session.query(Students).filter(Students.id == self._id).update(
            {key: value for key, value in self.data_to_update.items()},
            synchronize_session='fetch'  # Указываем, чтобы обновленная сессия синхронизировалась
        )

        # Сохраняем изменения в базе данных
        session.commit()

        if result == 0:
            raise KeyError("user not found")

        user = StudentsReader(_id=self._id).get
        return user

    def delete(self):
        result = session.query(Students).filter(Students.id == self._id).delete()
        session.commit()

        if result == 0:
            raise KeyError("user not found")

