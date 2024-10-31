
from werkzeug.exceptions import NotFound

from src.middleware.institute_middleware import InstitutesReader
from .groups_middleware import GroupsList
from .students_middleware import StudentsReader
from .validator import LevelGTO
from ..origin import *
from ..models import *

class GTOReader:
    """
    Класс для работы с данными по результатам ГТО (Готов к труду и обороне) студентов и групп в разрезе институтов.

    Этот класс позволяет получать результаты ГТО для отдельного студента, группы или всего института, а также
    предоставляет данные о количестве студентов с достижениями (золотой, серебряный и бронзовый уровни).

    Атрибуты:
    ----------
    institute_id : Union[int, None]
        Идентификатор института, к которому относятся группы или студенты.
    group_id : Union[int, None]
        Идентификатор группы, к которой относятся студенты (если требуется).
    student_id : Union[int, None]
        Идентификатор студента для выборки индивидуальных данных.
    institute : dict
        Данные об институте, полученные из `InstitutesReader`.
    groups : List[Dict]
        Список словарей с информацией о группах, принадлежащих институту.
    students : List[Dict]
        Список словарей с данными о студентах, относящихся к выбранным группам или группе.
    gto_results : Dict[str, int]
        Словарь для хранения количества золотых, серебряных и бронзовых достижений.

    Методы:
    -------
    compare_groups()
        Формирует список групп, относящихся к указанному `institute_id`.

    compare_students()
        Формирует список студентов, состоящих в указанных группах. Если задан `group_id`, отбирает студентов
        только из этой группы.

    compare_results()
        Формирует данные о результатах ГТО для студентов на текущий год по их уровню достижений.

    get_by_one_institute : property
        Выполняет операции для получения достижений всех студентов института.

    get_by_group : property
        Выполняет операции для получения достижений всех студентов указанной группы.

    get_by_student : property
        Возвращает данные о достижениях для конкретного студента.

    get_all_members : property
        Возвращает общее количество студентов с золотым, серебряным и бронзовым уровнями достижений.
    """
    def __init__(self, *,
                 institute_id:Union[int, None] = None,
                 group_id:Union[int, None] = None,
                 student_id:Union[int, None] = None):
        """
        Инициализирует объект `GTOReader` с заданными `institute_id`, `group_id` и `student_id`
        Параметры:
        ----------
        institute_id : Union[int, None]
            Идентификатор института для выборки данных (по умолчанию None).
        group_id : Union[int, None]
            Идентификатор группы для выборки данных (по умолчанию None).
        student_id : Union[int, None]
            Идентификатор студента для выборки данных (по умолчанию None).
        """
        self.institute_id = institute_id
        self.group_id = group_id
        self.student_id = student_id
        self.institute = InstitutesReader(self.institute_id).get
        self.groups: List[Dict] = []
        self.students: List[Dict] = []
        self.gto_results: Dict[str, int] = {"gold":0, "silver":0, "bronze":0}


    def compare_groups(self):
        """
        Формирует список групп, относящихся к указанному институту.

        Метод выполняет запрос для получения информации о всех группах, относящихся к `institute_id`,
        и сохраняет их в `self.groups`.
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
        Формирует список студентов, относящихся к указанным группам или одной группе.

        Если задан `group_id`, выбирает только студентов данной группы, иначе — студентов всех групп из `self.groups`.
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
        """
        Формирует данные о результатах ГТО для студентов за текущий год
        Если задан `student_id`, возвращает результаты для конкретного студента. В противном случае формирует данные
        о достижениях всех студентов из `self.students`.
        """
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
        """
        Возвращает достижения студентов института
        Метод вызывает `compare_groups()`, `compare_students()` и `compare_results()` для получения
        всех достижений по `institute_id`.
        """
        self.compare_groups()
        self.compare_students()
        self.compare_results()
        return self.gto_results

    @property
    def get_by_group(self):
        """
        Возвращает достижения студентов указанной группы
        Метод вызывает `compare_students()` и `compare_results()` для получения всех достижений по `group_id`.
        """
        self.compare_students()
        self.compare_results()
        return self.gto_results

    @property
    def get_by_student(self):
        """
        Возвращает достижения конкретного студента
        Метод вызывает `compare_results()` для получения достижений по `student_id`.
        """
        self.compare_results()
        return self.gto_results

    @property
    def get_all_members(self):
        """
        Возвращает общее количество достижений всех студентов
        Метод выполняет запросы для получения числа студентов с золотым, серебряным и бронзовым уровнями ГТО
        Возвращает:
        -----------
        Dict[str, int] : Словарь с количеством студентов по уровням достижений.
        """
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
        """
        Метод compare_rating в классе RatingByInstitute строит рейтинг институтов
        на основе уровней их достижений (золотой, серебряный и бронзовый) и
        определяет место конкретного института (self.institute_id) для каждого уровня,
        сохраняя позиции в словаре self.institute_rating.

        Создаются три списка (gold, silver, bronze) для каждого уровня достижений.
        Они будут содержать словари, в которых ключ — ID института,
        а значение — количество достижений (например, количество золотых медалей)
        для каждого института.

        Здесь метод перебирает все институты и, в зависимости от уровня (gold, silver, bronze),
        добавляет количество достижений каждого уровня в соответствующий список.
        Используется match для распределения данных по уровням.

        Каждый список (gold, silver, bronze) сортируется по убыванию количества достижений.
        Это позволяет определить рейтинг: институт с наибольшим количеством достижений
        окажется на первом месте.
        Для каждого уровня (аналогично для silver и bronze) метод проходит по отсортированному списку,
        и как только находит self.institute_id, записывает позицию в self.institute_rating.

        Таким образом, self.institute_rating в конце работы метода содержит позиции конкретного института
        в общем рейтинге по каждому уровню достижений.
        """
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
    """
    Класс для сбора и обработки данных о результатах ГТО (Готов к труду и обороне) для заданного института.
    Класс `AssemblerGTO` предназначен для агрегирования данных о количестве достижений по уровням (золото, серебро, бронза),
    общем количестве участников, рейтинговой позиции института по уровням, а также расчета процентного соотношения достижений.
    Атрибуты:
    ----------
    institute_id : int
        Идентификатор института, для которого собираются данные.
    gto_results : Dict[str, int]
        Словарь, содержащий количество достижений института по уровням: золотые, серебряные и бронзовые медали.
    rating : Dict[str, int]
        Словарь с рейтингом института для каждого уровня достижений (золото, серебро, бронза).
    all_members : Dict[str, int]
        Словарь, содержащий общее количество участников института, сдававших ГТО по каждому уровню (золото, серебро, бронза).
    data : Dict
        Основной словарь, содержащий информацию о количестве достижений, числе участников, рейтинге и процентном распределении
        по уровням.
    Методы:
    -------
    __init__(self, *, institute_id: int)
        Инициализирует объект `AssemblerGTO` для заданного `institute_id`, запрашивает данные о достижениях, участниках и
        рейтинге, формирует базовую структуру данных.
    get(self) -> Dict
        Свойство, возвращающее готовый словарь с обработанными данными. Если общее количество достижений не равно нулю,
        рассчитывает процентное соотношение для каждого уровня достижений (золото, серебро, бронза).
    """
    def __init__(self, *,institute_id:int):
        """
        Инициализирует объект `AssemblerGTO` с заданным идентификатором института, собирает данные о достижениях,
        участниках и рейтинге
        Параметры:
        ----------
        institute_id : int
            Идентификатор института, для которого будут собраны и обработаны данные
        Создает:
        --------
        - self.gto_results : данные о достижениях (медали) для указанного института.
        - self.rating : рейтинг института для каждого уровня достижений.
        - self.all_members : количество участников от института по каждому уровню.
        - self.data : основной словарь, включающий собранные данные и их процентное распределение.
        """
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
        """
        Возвращает основной словарь `data`, содержащий собранные данные о результатах и рейтинге института
        Если общее количество достижений (золотые, серебряные и бронзовые медали) не равно нулю, рассчитывает процентное
        соотношение для каждого уровня
        Возвращает:
        -----------
        Dict : Словарь `data`, включающий следующие ключи:
            - "count_by_institute" : Количество достижений по уровням (золото, серебро, бронза).
            - "members_count" : Общее число участников для каждого уровня.
            - "rating" : Позиция института в рейтинге для каждого уровня.
            - "percent_by_common" : Процентное соотношение достижений по каждому уровню.
        """
        if self.gto_results["gold"]+self.gto_results["silver"]+self.gto_results["bronze"]!=0:
            for i in ["gold","silver","bronze"]:
                self.data["percent_by_common"][i] = self.gto_results[i]/(
                    self.gto_results["gold"]+self.gto_results["silver"]+self.gto_results["bronze"]
                )*100
        return self.data

class GTOWriter:
    """
    Класс для записи и обновления данных о результатах ГТО (Готов к труду и обороне) студента в базе данных.
    Класс `GTOWriter` предоставляет методы для добавления новой записи с уровнем достижения студента
    в ГТО и обновления существующей записи на текущий год.
    Атрибуты:
    ----------
    student_id : int
        Идентификатор студента, для которого записываются результаты ГТО.
    level : str
        Уровень достижения студента в ГТО (например, золотой, серебряный, бронзовый), преобразованный с использованием `LevelGTO`.
    Методы:
    -------
    __init__(self, *, student_id: int, level: str)
        Инициализирует объект `GTOWriter` для заданного студента и уровня ГТО, преобразует уровень с помощью `LevelGTO`.
    write(self) -> Dict
        Добавляет новую запись о результатах ГТО в базу данных для указанного студента и текущего года.
    update(self) -> Dict
        Обновляет запись о результате ГТО для указанного студента и текущего года, если она существует в базе данных.
        Если запись не найдена, вызывает исключение `NoResultFound`.
    """
    def __init__(self, *,
                 student_id: int,
                 level: str
                 ):
        """
        Инициализирует объект `GTOWriter` с заданными `student_id` и `level`
        Параметры:
        ----------
        student_id : int
            Уникальный идентификатор студента, для которого будут добавлены или обновлены данные ГТО.
        level : str
            Уровень достижения ГТО (например, "gold", "silver", "bronze"), который преобразуется через `LevelGTO`
        Создает:
        --------
        - self.student_id : сохраняет идентификатор студента.
        - self.level : преобразует и сохраняет уровень достижения студента в ГТО.
        """
        self.student_id = student_id
        self.level = LevelGTO(level).get

    def write(self):
        """
        Добавляет новую запись о результатах ГТО в базу данных для указанного студента и текущего года.

        Метод создает объект `BaseGTO`, устанавливает текущий год, добавляет объект в сессию и сохраняет изменения.
        В случае ошибки откатывает изменения и вызывает исключение.

        Возвращает:
        -----------
        Dict : Словарь с `student_id` и `level`, если запись успешно добавлена.

        Исключения:
        -----------
        ValueError : Если данные некорректны или добавление записи невозможно.
        """
        gto = BaseGTO(
            student_id=self.student_id,
            level=self.level,
            year=datetime.now().year
        )
        try:
            session.add(gto)  # Добавляем объект в сессию
            session.commit()  # Сохраняем изменения в базе данных
        except Exception as e:
            session.rollback()
            raise ValueError("incorrect data")
        return {"student_id":self.student_id, "level":self.level}

    def update(self):
        """
        Обновляет существующую запись о результате ГТО для текущего года.

        Метод проверяет наличие записи о достижениях студента в текущем году.
        Если запись найдена, обновляет уровень, сохраняет изменения в базе данных. В случае ошибки откатывает изменения.

        Возвращает:
        -----------
        Dict : Словарь с `student_id` и обновленным `level`, если запись успешно обновлена.

        Исключения:
        -----------
        ValueError : Если данные некорректны или обновление невозможно.
        NoResultFound : Если запись о результате ГТО для текущего года не найдена.
        """
        gto = session.query(BaseGTO).filter(
            (BaseGTO.student_id == self.student_id) &
            (BaseGTO.year == int(datetime.now().year))
        ).one_or_none()

        if gto:
            gto.level = self.level
            try:                # Обновляем уровень
                session.commit()  # Сохраняем изменения
            except Exception as e:
                session.rollback()
                raise ValueError("incorrect data")
            return {"student_id": self.student_id, "level": self.level}
        else:
            raise NoResultFound(f"{self.student_id} not found.")



