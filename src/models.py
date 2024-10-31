from sqlalchemy import create_engine, Column, Integer, Text, Boolean, ForeignKey, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import NoResultFound
from .settings import DBSettings

Base = declarative_base()

# Настройка подключения к БД
if DBSettings.DB_KIND == "sqlite":
    engine = create_engine(f"sqlite:///src/{DBSettings.DB_NAME}.db")
else:
    engine = create_engine(DBSettings.uri)

Session = sessionmaker(bind=engine)
session = Session()


# Модель Tokens
class Tokens(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)


# Модель Users
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True)
    email = Column(Text, unique=True)
    is_active = Column(Boolean)
    password_hash = Column(Text)
    full_name = Column(Text)
    is_superuser = Column(Boolean)


# Модель Institutes
class Institutes(Base):
    __tablename__ = "institutes"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(Text)
    groups = relationship("Groups", order_by="Groups.id", back_populates="institute")


# Модель Groups
class Groups(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, unique=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    course = Column(Integer)
    name = Column(Text, unique=True)
    institute = relationship("Institutes", back_populates="groups")
    students = relationship("Students", order_by="Students.id", back_populates="group")


# Модель Students
class Students(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, unique=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    course = Column(Integer)
    first_name = Column(Text)
    last_name = Column(Text)
    birth_date = Column(String)
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
    group = relationship("Groups", back_populates="students")
    results = relationship("StandardResults", order_by="StandardResults.id", back_populates="student")
    theory_results = relationship("TheoryResults", order_by="TheoryResults.id", back_populates="student")


# Модель GTO
class BaseGTO(Base):
    __tablename__ = "gto"

    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    level = Column(Text)
    year = Column(Integer)


# Модель Standard
class Standard(Base):
    __tablename__ = "standard"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(Text)
    results = relationship("StandardResults", order_by="StandardResults.id", back_populates="standard")


# Модель StandardResults
class StandardResults(Base):
    __tablename__ = "standard_results"

    id = Column(Integer, primary_key=True, unique=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    standard_id = Column(Integer, ForeignKey('standard.id'))
    semester = Column(Integer)
    result = Column(Integer)
    student = relationship("Students", back_populates="results")
    standard = relationship("Standard", back_populates="results")


# Модель Theory
class Theory(Base):
    __tablename__ = "theory"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(Text)
    results = relationship("TheoryResults", back_populates="theory")


# Модель TheoryResults
class TheoryResults(Base):
    __tablename__ = "theory_results"

    id = Column(Integer, primary_key=True, unique=True)
    theory_id = Column(Integer, ForeignKey('theory.id'))
    student_id = Column(Integer, ForeignKey('students.id'))
    semester = Column(Integer)
    result = Column(Integer)
    theory = relationship("Theory", back_populates="results")
    student = relationship("Students", back_populates="theory_results")


# Создание всех таблиц
Base.metadata.create_all(engine)

