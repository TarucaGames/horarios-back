from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    Sequence,
    String,
    Index,
    DateTime,
)
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

# DATABASE MODELS


class EmployeeDB(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    surname = Column(String)
    code = Column(String)
    color = Column(String)
    active = Column(Boolean, default=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    nickname = Column(String)

    user = relationship(
        "UserDB", back_populates="employee"
    )  # Relationship back to User


class DepartmentDB(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)


class Shift2DB(Base):
    __tablename__ = "shifts2"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    start_time = Column(String)
    end_time = Column(String)
    date = Column(String)
    week = Column(String)
    is_holiday = Column(Boolean, default=False)


class ShiftDB(Base):
    __tablename__ = "shifts"

    id = Column(Integer, Sequence("shift_id_sequence"), autoincrement=True)
    date = Column(Date)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    start_time = Column(String)
    end_time = Column(String)
    week = Column(Integer)
    type = Column(Integer)

    def __repr__(self):
        return f"<Shift(date={self.date}, employee_id={self.employee_id}, hours={self.hours})>"

    __table_args__ = (PrimaryKeyConstraint("date", "employee_id"),)


class ShiftDBObj(Base):
    __tablename__ = "shifts_db"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    text = Column(String)
    description = Column(String)
    week = Column(String)
    type = Column(Integer, default=1)

    employee = relationship("EmployeeDB", backref="shifts", lazy=True)

    __table_args__ = (Index("ix_employee_id_start_date", "employee_id", "start_date"),)


class TestObjDB(Base):
    __tablename__ = "test_obj"

    id = Column(Integer, Sequence("shift_id_seq"), autoincrement=True)
    date = Column(Date)
    employee_id = Column(Integer)
    hours = Column(Integer)

    def __repr__(self):
        return f"<Shift(date={self.date}, employee_id={self.employee_id}, hours={self.hours})>"

    __table_args__ = (PrimaryKeyConstraint("date", "employee_id"),)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    employee_id = Column(
        Integer, ForeignKey("employees.id"), nullable=True
    )  # Link to EmployeeDB

    employee = relationship(
        "EmployeeDB", back_populates="user"
    )  # Define relationship with EmployeeDB


# DATA MODELS


class DepartmentModel(BaseModel):
    id: Optional[int]
    name: str


class EmployeeModel(BaseModel):
    id: Optional[int]
    name: str
    surname: str
    code: str
    color: str
    active: bool
    department: DepartmentModel
    nickname: str


class ShiftModel(BaseModel):
    employee_id: Optional[EmployeeModel]
    start_time: Optional[str]
    end_time: Optional[str]
    date: Optional[str]
    week: Optional[str]
    is_holiday: Optional[bool]


class CreateShiftModel(BaseModel):
    employee_id: Optional[int]
    start_time: Optional[str]
    end_time: Optional[str]
    date: Optional[str]
    week: Optional[str]
    is_holiday: Optional[bool]


class TestObjModel(BaseModel):
    date: str
    employee_id: int
    hours: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class EmployeeCreate(BaseModel):
    name: str
    code: str
    color: str
    active: bool = True
    department_id: int = 1
    nickname: str = ""


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    code: Optional[str] = None
    color: Optional[str] = None
    active: Optional[bool] = None
    department_id: Optional[int] = None
    nickname: Optional[str] = None


class ShiftCreate(BaseModel):
    date: str
    employee_id: int
    start_time: str
    end_time: Optional[str]
    week: int
    type: int = 1
    # Work: 1, Holiday: 2, Free: 3


class ShiftCreateObj(BaseModel):
    employee_id: int
    start_date: datetime
    end_date: Optional[datetime]
    text: str
    description: str
    week: int
    type: int = 1
    # Work: 1, Holiday: 2, Free: 3


class MultipleShiftCreateObj(BaseModel):
    shifts: List[ShiftCreateObj]


class MultipleShiftCreate(BaseModel):
    shifts: List[ShiftCreate]


class EmployeeResponse(BaseModel):
    id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
    code: Optional[str]
    color: Optional[str]
    active: Optional[bool]
    # department: Optional[DepartmentModel]
    nickname: Optional[str]


class ShiftEmployeeResponse(BaseModel):
    id: int
    name: str
    surname: Optional[str]
    nickname: Optional[str]


class ShiftResponse(BaseModel):
    id: int
    employee_id: int
    employee: ShiftEmployeeResponse
    start_date: datetime
    end_date: datetime
    text: str
    description: str
    week: int
    type: int


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
