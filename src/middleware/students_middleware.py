from typing import Union
from unittest import case

from .validator import (
    Validator, FullName, Patronymic,
    Date, Sex, MedicalGroup, Height,
    Weight, Email, Phone, Year,
    BirthPlace, Address, Id
)
from ..origin import *

from peewee import DoesNotExist, IntegrityError

from .groups_middleware import GroupsReader
#from .institute_middleware import InstitutesReader
from ..models import Students, Groups, session, NoResultFound


class StudentsReader:
    """
    Класс `StudentsReader` предназначен для чтения данных о студентах и их преобразования в словарь.
    Поддерживает поиск по ID студента или по имени и ID группы.

    Параметры:
    ----------
    _id : int, optional
        ID студента для поиска и извлечения данных.

    name : str, optional
        Полное имя студента, если поиск выполняется по имени и ID группы. Формат: "Имя Фамилия".

    group_id : int, optional
        ID группы для поиска, используется вместе с именем студента.

    email : str, optional
        Электронная почта студента. Не используется в текущей версии, но оставлена для возможных расширений.

    Исключения:
    -----------
    - Не рекомендуется передавать одновременно ID студента и пару "имя + ID группы", так как это может
      привести к неопределенному поведению.

    Атрибуты:
    ----------
    student : object
        Объект данных студента, если он найден.

    group : dict
        Словарь с информацией о группе студента, если он найден.

    Методы:
    -------
    get -> Union[Dict, None]:
        Возвращает словарь с данными студента, если он найден, иначе вызывает исключение `NoResultFound`.

    Примеры:
    --------
    - Поиск по ID:
        >>> student_reader = StudentsReader(_id=1)
        >>> student_reader.get

    - Поиск по имени и ID группы:
        >>> student_reader = StudentsReader(name="Иван Иванов", group_id=2)
        >>> student_reader.get

    Исключения:
    -----------
    NoResultFound:
        Вызывается при отсутствии данных по заданным критериям.
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
        """
        Возвращает данные студента в виде словаря, если он найден.

        Возвращаемый словарь содержит основную информацию о студенте и его группе.

        Возвращает:
        ----------
        Union[Dict, None]
            Словарь с данными студента. Возвращает None, если данные не найдены.

        Исключения:
        -----------
        NoResultFound:
            Вызывается, если ID студента не найден.
        """
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
        raise NoResultFound("incorrect id of user")


class StudentsList:
    def __init__(self, *,
                 institute_id: Union[int, None]=None,
                 group_id: Union[int, str]=None,
                 name:Union[str,None]=None,
                 skip=0,
                 limit=100
                 ):
        """
        Класс `StudentsList` предоставляет возможность формирования списка студентов по различным критериям,
        включая ID института, ID группы или имя студента с указанием ID группы.

        Параметры:
        ----------
        institute_id : int, optional
            ID института для фильтрации студентов, связанных с указанным институтом.

        group_id : int или str, optional
            ID группы для фильтрации студентов, входящих в эту группу.

        name : str, optional
            Полное имя студента (формат: "Имя Фамилия"), используется в сочетании с group_id для точного поиска студента.

        skip : int, default=0
            Количество записей, которые нужно пропустить в начале списка.

        limit : int, default=100
            Максимальное количество записей, которые будут возвращены.

        Атрибуты:
        ----------
        students : Union[None, List[Dict]]
            Список словарей с данными студентов, которые соответствуют критериям фильтрации.
            Если критерии не указаны, будет `None`.

        count : int
            Общее количество студентов, доступное в базе данных.

        Методы:
        -------
        _make_list()
            Формирует список студентов, соответствующих заданным критериям.
            В зависимости от указанных параметров фильтрации, возвращает студентов по институту,
            по группе или по имени и группе.

        Примеры:
        --------
        Создание списка студентов по ID института:
            >>> students_list = StudentsList(institute_id=5)
            >>> students_list._make_list()

        Создание списка студентов по ID группы:
            >>> students_list = StudentsList(group_id=3)
            >>> students_list._make_list()

        Создание списка студентов по имени и ID группы:
            >>> students_list = StudentsList(name="Иван Иванов", group_id=2)
            >>> students_list._make_list()
        """
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
        """
        Формирует список студентов, соответствующих заданным критериям фильтрации.

        В зависимости от указанных параметров (institute_id, group_id, имя и фамилия с group_id),
        список студентов будет включать только тех, кто соответствует условиям фильтрации.

        Если указан ID института, включаются студенты, связанные с этим институтом.
        Если указан ID группы, включаются только студенты из данной группы.
        Если указаны имя, фамилия и ID группы, включаются только студенты, соответствующие этим данным.
        """
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
        """
        Класс `StudentWriter` предназначен для создания, обновления и удаления данных о студентах.
        Входные данные проходят проверку и валидацию перед записью в базу данных.

        Параметры:
        ----------
        _id : int, optional
            Идентификатор студента. Используется при обновлении или удалении записи о студенте.

        data : dict, optional
            Словарь с данными студента. Ключи словаря должны совпадать с именами полей в базе данных.
            Поддерживаемые ключи включают: `first_name`, `last_name`, `patronymic`, `birth_date`, `sex`,
            `medical_group`, `height`, `weight`, `email`, `phone_number`, `admission_year`, `birth_place`,
            `address`, `group_id`, `course`.

        Атрибуты:
        ----------
        data_to_update : dict
            Словарь с данными, подготовленными для записи или обновления в базе данных после валидации.

        Методы:
        -------
        validate_data(data)
            Проверяет входные данные на корректность, преобразует и добавляет их в `data_to_update`.

        write()
            Добавляет нового студента в базу данных на основе валидированных данных из `data_to_update`.

        update()
            Обновляет существующие данные студента, найденного по `_id`.

        delete()
            Удаляет запись студента, найденного по `_id`, из базы данных.

        Исключения:
        -----------
        ValueError
            Если переданы некорректные данные.

        IntegrityError
            Если попытка создать или обновить запись вызывает конфликт целостности данных (например, студент уже существует).

        KeyError
            Если студент с заданным `_id` не найден при обновлении или удалении.

        Примеры:
        --------
        Создание нового студента:
            >>> student_data = {"first_name": "Иван", "last_name": "Иванов", "birth_date": "2000-01-01", ...}
            >>> student_writer = StudentWriter(data=student_data)
            >>> new_student = student_writer.write()

        Обновление существующего студента:
            >>> student_data = {"first_name": "Петр", "last_name": "Петров", ...}
            >>> student_writer = StudentWriter(_id=123, data=student_data)
            >>> updated_student = student_writer.update()

        Удаление студента:
            >>> student_writer = StudentWriter(_id=123)
            >>> student_writer.delete()
        """
        self._id = _id
        self.data = data
        self.data_to_update: Dict[str, Union[int, str]] = {}
        self.validate_data(self.data)

    def validate_data(self, data:Dict[str,Union[int,str]]):
        """
        Проверяет и валидирует входные данные студента. Поддерживаемые ключи данных:
        `first_name`, `last_name`, `patronymic`, `birth_date`, `sex`, `medical_group`, `height`, `weight`,
        `email`, `phone_number`, `admission_year`, `birth_place`, `address`, `group_id`, `course`.

        Параметры:
        ----------
        data : dict
            Словарь с данными студента, где ключи - это поля студента,
            а значения - соответствующие значения этих полей.

        Исключения:
        -----------
        ValueError
            Если передан некорректный ключ в `data`.
        """
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
                case "course":
                    self.data_to_update["course"] = Id(value).get
                case _:
                    raise ValueError("invalid data")

    def write(self):
        """
        Добавляет нового студента в базу данных на основе валидированных данных из `data_to_update`.

        Возвращает:
        ----------
        dict
            Словарь с данными добавленного студента.

        Исключения:
        -----------
        IntegrityError
            Если студент уже существует.
        """
        student = Students(**self.data_to_update) # Создание экземпляра студента
        try:
            session.add(student)  # Добавляем объект в сессию
            session.commit()
        except Exception as e:
            session.rollback()
            raise IntegrityError("student already exists")
        user = StudentsReader(
            name=f"{self.data_to_update["first_name"]} {self.data_to_update['last_name']}",
            group_id=self.data_to_update['group_id']
        ).get
        return user

    def update(self):
        """
        Обновляет данные студента, найденного по `_id`.

        Возвращает:
        ----------
        dict
            Словарь с обновленными данными студента.

        Исключения:
        -----------
        ValueError
            Если студент уже существует.

        KeyError
            Если студент с заданным `_id` не найден.
        """
        result = session.query(Students).filter(Students.id == self._id).update(
            {key: value for key, value in self.data_to_update.items()},
            synchronize_session='fetch'  # Указываем, чтобы обновленная сессия синхронизировалась
        )

        # Сохраняем изменения в базе данных
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError("student already exists")

        if result == 0:
            raise KeyError("user not found")

        user = StudentsReader(_id=self._id).get
        return user

    def delete(self):
        """
        Удаляет студента, найденного по `_id`, из базы данных.

        Исключения:
        -----------
        KeyError
            Если студент с заданным `_id` не найден.
        """
        result = session.query(Students).filter(Students.id == self._id).delete()
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise KeyError("user not found")
        if result == 0:
            raise KeyError("user not found")

