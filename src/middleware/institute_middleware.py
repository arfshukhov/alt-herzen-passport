import json
from typing import *

from peewee import DoesNotExist

from src.models import Institutes, NoResultFound, session


class InstitutesReader:
    """
    Класс `InstitutesReader` предназначен для чтения данных из таблицы институтов по идентификатору.
    Он позволяет получать информацию об институте, используя его ID.

    Параметры:
    ----------
    _id : int
        Идентификатор института, по которому осуществляется поиск.

    Атрибуты:
    ----------
    institute : Union[str, None]
        Объект института, полученный из базы данных. Если институт с данным ID не найден,
        значение будет равно None.

    Методы:
    -------
    get
        Возвращает словарь с данными института, если он найден, или None в противном случае.

    Примеры:
    --------
    >>> institute_reader = InstitutesReader(_id=1)
    >>> institute_data = institute_reader.get
    >>> print(institute_data)  # {'name': 'Институт технологий', 'id': 1}
    """
    institute: Union[str, None]

    def __init__(self,
                 _id: int):
        """
        Инициализирует экземпляр класса `InstitutesReader` и выполняет запрос к базе данных
        для получения информации о институте по его ID.

        Параметры:
        ----------
        _id : int
            Идентификатор института, который будет использоваться для выполнения запроса.

        Исключения:
        -----------
        NoResultFound
            Вызывается, если нет записей, соответствующих заданному идентификатору.
        """
        try:
            self.institute = session.query(Institutes).filter(Institutes.id == _id).one_or_none()
        except NoResultFound:
            self.institute = None


    @property
    def get(self) -> Union[dict, None]:
        """
        Возвращает информацию об институте в виде словаря, если институт найден.
        В противном случае возвращает None.

        Возвращает:
        ----------
        dict
            Словарь с данными института (название и идентификатор) или None, если институт не найден.
        """
        if not self.institute:
            return None
        return {"name":self.institute.name,
                "id":self.institute.id,
                }
    
class InstitutesList:
    """
    Класс `InstitutesList` предназначен для получения списка институтов по заданному диапазону их идентификаторов.
    Он позволяет извлекать информацию об институтах, пропуская определённое количество записей и ограничивая общее число выводимых записей.

    Параметры:
    ----------
    skip : int
        Количество записей, которые нужно пропустить перед началом выборки.

    limit : int
        Максимальное количество записей, которые будут возвращены в результате.

    Методы:
    -------
    _make_list()
        Заполняет список институтов, основываясь на диапазоне ID.

    get
        Возвращает список институтов, соответствующих заданному диапазону.

    Примеры:
    --------
    >>> institutes_list = InstitutesList(skip=0, limit=10)
    >>> institute_data = institutes_list.get
    >>> print(institute_data)  # [{'name': 'Институт технологий', 'id': 1}, ...]
    """
    def __init__(self,
                 skip:int,
                 limit:int):
        """
        Инициализирует экземпляр класса `InstitutesList` с заданными параметрами `skip` и `limit`.

        Параметры:
        ----------
        skip : int
            Количество записей, которые будут пропущены.

        limit : int
            Максимальное количество институтов, которые будут возвращены.
        """
        self.skip = skip
        self.limit = limit
        self.institutes_list: List[Dict] = []

    def _make_list(self):
        """
        Заполняет `institutes_list` данными институтов на основе диапазона их ID.
        Если института с данным ID не существует, он не добавляется в список.
        """
        for i in range(self.skip+1, self.limit+self.limit+2):
            institute = InstitutesReader(_id=i).get
            if institute:
                self.institutes_list.append(institute)

    @property
    def get(self)->List[Dict]:
        """
        Возвращает список институтов, соответствующих заданному диапазону.
        Вызывает метод `_make_list()` для заполнения списка.

        Возвращает:
        ----------
        List[Dict]
            Список институтов, каждый из которых представлен в виде словаря с данными.
        """
        self._make_list()
        return self.institutes_list