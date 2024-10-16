import hashlib
import re
from typing import Union, Any, override


class Validator:
    """
    Родительский класс для всех валидаторов данных
    Как результат работы выводит либо заданное значние,
    либо строку 'invalid'
    """
    def __init__(self, *arg:Any):
        self.data = self.validate(*arg)

    def validate(self, data: Any) -> str:
        ...

    @property
    def get(self) -> str:
        return str(self.validate(self.data))


class Email(Validator):
    def __init__(self, email:str):
        super().__init__(email)

    @override
    def validate(self, data: str) -> str:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if 1 <= len(data) <= 30 and re.match(pattern, data):
            return data
        else:
            return "invalid"

class FullName(Validator):
    def __init__(self, name:str):
        super().__init__(name)

    def _filter(self, data: str) -> Union[str, bool]:
        pattern = r'^[А-Яа-яЁё\s-]+$'
        if 1 <= len(data) <= 30 and re.match(pattern, data):
            return data
        else:
            return 0

    @override
    def validate(self, data: str) -> str:
        is_valid= map(self._filter, data.split())
        if all(is_valid):
            return data
        else:
            return "invalid"

class Phone(Validator):
    def __init__(self, phone:str):
        if phone.startswith("8"):
            phone = phone.replace("8", "+7", 1)
        super().__init__(phone)

    @override
    def validate(self, data: str) -> str:
        pattern = r'^\+\d{1,20}$'
        if re.match(pattern, data):
            return data
        else:
            return "invalid"

class Password(Validator):
    def __init__(self, password:str):
        super().__init__(password)

    @override
    def validate(self, data: str) -> str:
        hash_object = hashlib.sha256()

        # Обновление объекта хэширования данными
        hash_object.update(bytes(data, "utf-8"))
        password_hash = str(hash_object.hexdigest())

        # Получение хэша в шестнадцатеричном формате
        return password_hash

