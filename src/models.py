from sqlalchemy import create_engine, Column, Integer, Text, Boolean, ForeignKey, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Relationship
from sqlalchemy.exc import NoResultFound
from .settings import DBSettings



Base = declarative_base()

"""
для локального запуска удобнее исользовать SQLite
для того, чтобы подключиться к БД Postgres
в переменной окружения DB_KIND
должно быть что-то отличное от
'sqlite'
"""
if DBSettings.DB_KIND == "sqlite":
    engine = create_engine(f"sqlite:///src/{DBSettings.DB_NAME}.db")
else:
    engine = create_engine(DBSettings.uri)

Session = sessionmaker(bind=engine)
session = Session()


# Таблица пользователей
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True)
    email = Column(Text, unique=True)
    is_active = Column(Boolean)
    password_hash = Column(Text)
    full_name = Column(Text)
    is_superuser = Column(Boolean)


# Таблица институтов
class Institutes(Base):
    __tablename__ = "institutes"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(Text)
    groups = relationship("Groups", order_by="Groups.id", back_populates="institute")
    students = relationship("Students", order_by="Students.id", back_populates="institute")


# Таблица групп
class Groups(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, unique=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    course = Column(Integer)
    name = Column(Text, unique=True)
    institute = relationship("Institutes", back_populates="groups")
    students = relationship("Students", order_by="Students.id", back_populates="group")


# Таблица студентов
class Students(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, unique=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    course = Column(Integer)
    first_name = Column(Text)
    last_name = Column(Text)
    birth_date = Column(Date)
    birth_place = Column(Text)
    email = Column(Text, unique=True)
    phone_number = Column(Text, unique=True)
    sex = Column(Text)
    medical_group = Column(Text)
    address = Column(Text)
    admission_year = Column(Integer)
    weight = Column(Integer)
    height = Column(Integer)
    patronymic = Column(Text)
    institute = relationship("Institutes", back_populates="students")
    group = relationship("Groups", back_populates="students")
    results = relationship("StandardResults", order_by="StandardResults.id", back_populates="student")


# Таблица GTO
class BaseGTO(Base):
    __tablename__ = "gto"

    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    level = Column(Text)
    year = Column(Integer)


# Таблица нормативов
class Standard(Base):
    __tablename__ = "standard"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(Text)
    result = relationship("StandardResults", order_by="StandardResults.id", back_populates="standard")


# Таблица результатов нормативов
class StandardResults(Base):
    __tablename__ = "standard_results"

    id = Column(Integer, primary_key=True, unique=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    standard_id = Column(Integer, ForeignKey('standard.id'))
    semester = Column(Integer)
    result = Column(Integer)
    student = relationship("Students", back_populates="results")
    standard = relationship("Standard", back_populates="results")


# Таблица теории
class Theory(Base):
    __tablename__ = "theory"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(Text)
    result = Relationship("TheoryResults", back_populates="theory")


# Таблица результатов теории
class TheoryResults(Base):
    __tablename__ = "theory_results"

    id = Column(Integer, primary_key=True, unique=True)
    theory_id = Column(Integer, ForeignKey('theory.id'))
    student_id = Column(Integer, ForeignKey('students.id'))
    result = Column(Integer)
    theory = relationship("Theory", back_populates="results")
    student = relationship("Students", back_populates="results")

# Создание всех таблиц
Base.metadata.create_all(engine)

