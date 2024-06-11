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
)
from database import Base


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


class TestObjDB(Base):
    __tablename__ = "test_obj"

    id = Column(Integer, Sequence("shift_id_seq"), autoincrement=True)
    date = Column(Date)
    employee_id = Column(Integer)
    hours = Column(Integer)

    def __repr__(self):
        return f"<Shift(date={self.date}, employee_id={self.employee_id}, hours={self.hours})>"

    __table_args__ = (PrimaryKeyConstraint("date", "employee_id"),)


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


class ShiftCreate(BaseModel):
    date: str
    employee_id: int
    start_time: str
    end_time: Optional[str]
    week: int
    type: int = 1
    # Work: 1, Holiday: 2, Free: 3


class MultipleShiftCreate(BaseModel):
    shifts: List[ShiftCreate]
