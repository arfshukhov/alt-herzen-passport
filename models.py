from peewee import *


from settings import DBSettings


"""
для локального запуска удобнее исользовать SQLite
для того, чтобы подключиться к БД Postgres
в переменной окружения DB_KIND
должно быть что-то отличное от
'sqlite'
"""
if DBSettings.DB_KIND == "sqlite":
    db = SqliteDatabase(DBSettings.DB_NAME+".db")
else:
    db = PostgresqlDatabase(DBSettings.uri)


"""
Таблица пользоваталей
"""
class Users(Model):
    id = IntegerField(unique=True, primary_key=True)
    email = TextField(unique=True)
    is_active = BooleanField()
    password_hash = TextField()
    full_name = TextField()
    is_superuser = BooleanField()

    class Meta:
        database = db
        db_table = "users"


"""
Таблица с институтами
"""
class Institutes(Model):
    id = IntegerField(unique=True, primary_key=True)
    name = TextField()

    class Meta:
        database = db
        db_table = "institutes"


"""
Таблица с группами
"""
class Groups(Model):
    id = IntegerField(unique=True, primary_key=True)
    institute_id = ForeignKeyField(Institutes, backref="groups")
    name = TextField()

    class Meta:
        database = db
        db_table = "groups"


"""
Таблица со студентами 
"""
class Students(Model):
    id = IntegerField(unique=True, primary_key=True)
    institute_id = ForeignKeyField(Institutes, backref="students")
    group_id = ForeignKeyField(Groups, backref="students")
    course = IntegerField()
    first_name = TextField()
    last_name = TextField()
    birth_date = DateField()
    email = TextField()
    phone_number = TextField(unique=True)
    sex = TextField()
    medical_group = TextField()
    address = TextField()
    admission_year = IntegerField()
    weight = IntegerField()
    height = IntegerField()

    class Meta:
        database = db
        db_table = "students"



