import hashlib
import re
from datetime import datetime
from typing import Union, Any, override

from werkzeug.routing import ValidationError


class Validator:
    """
    Родительский класс для всех валидаторов данных
    Как результат работы выводит либо заданное значние,
    либо строку 'invalid'
    """
    def __init__(self, arg:Any):
        self.data = arg

    def validate(self, data: Any) -> str:
        ...

    @property
    def get(self) -> str:
        return self.validate(self.data)


class Email(Validator):
    def __init__(self, email:str):
        super().__init__(email)

    @override
    def validate(self, data: str) -> str:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if 1 <= len(data) <= 30 and re.match(pattern, data):
            return data
        else:
            raise ValidationError(f'Invalid email: {data}')


class FullName(Validator):
    def __init__(self, name:str):
        super().__init__(name)

    def _filter(self, data: str) -> str:
        pattern = r'^[А-Яа-яЁё\s-]+$'
        if 1 <= len(data) <= 40 and re.match(pattern, data):
            return data
        else:
            raise ValidationError(f'Invalid full name: {data}')

    @override
    def validate(self, data: str) -> str:
        is_valid= map(self._filter, data.split())
        if all(is_valid):
            return data
        else:
            raise ValidationError(f'Invalid full name: {data}')


class Patronymic(Validator):
    def __init__(self, patronymic:str):
        super().__init__(patronymic)

    @override
    def validate(self, data: str) -> str:
        pattern = r'^[А-Яа-яЁё\s-]+$'
        if data.isspace() or re.match(pattern, data):
            return data
        else:
            raise ValidationError(f'Invalid full name: {data}')


class Date(Validator):
    def __init__(self, date: str):
        super().__init__(date)

    @override
    def validate(self, data: str) -> str:
        date_pattern = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
        if re.match(date_pattern, data):
            return datetime.strptime(data, '%Y-%m-%d').date()  # Исправлено
        else:
            raise ValidationError(f'Invalid date: {data} date must be in format YYYY-MM-DD')



class Sex(Validator):
    def __init__(self, sex:str):
        super().__init__(sex)

    @override
    def validate(self, data: str) -> str:
        if data in ["Мужской", "Женский"]:
            return data
        else:
            raise ValidationError("sex must be 'Мужской' or 'Женский'")


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
            raise ValidationError(f'Invalid phone: {data}')


class Password(Validator):
    def __init__(self, password:str):
        super().__init__(password)

    @override
    def validate(self, data: str) -> str:
        self.cryptor = hashlib.sha256()
        self.cryptor.update(bytearray(data.encode()))
        return str(self.cryptor.hexdigest())


class LevelGTO(Validator):
    def __init__(self, level_gto:str):
        super().__init__(level_gto)

    @override
    def validate(self, data: str) -> str:
        if data in ["gold", "silver", "bronze"]:
            return data
        else:
            raise ValidationError(f'Invalid level_gto: {data}. It must be in'
                                  f'["gold", "silver", "bronze"]')


class MedicalGroup(Validator):
    def __init__(self, medical_group:str):
        super().__init__(medical_group)

    @override
    def validate(self, data: str) -> str:
        groups = ["Основная", "Подготовительная",
                    "Специальная \"А\" (оздоровительная)", "Специальная \"Б\" (реабилитационная)"]
        if data in groups:
            return data
        else:
            raise ValidationError(f'Invalid medical group: {data}, must be in {str(groups)}')


class Height(Validator):
    def __init__(self, height: int):
        super().__init__(height)

    @override
    def validate(self, data: int) ->int:
        if isinstance(data, int) and data > 0:
            return data
        else:
            raise ValidationError(f'Invalid: {data}, must be an integer and greater than 0')


class Weight(Height):
    ...


class Year(Height):
    ...


class BirthPlace(Validator):
    def __init__(self, birth_place:str):
        super().__init__(birth_place)

    @override
    def validate(self, data: str) -> str:
        if isinstance(data, str) and not data.isspace():
            return data
        else:
            raise ValidationError(f'Invalid data: {data}')


class Address(BirthPlace):
    def __init__(self, address:str):
        super().__init__(address)


class Id(Height):
    ...