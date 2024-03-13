import json
from fastapi import FastAPI, File, HTTPException, Depends, UploadFile
from psycopg2 import IntegrityError
from pydantic import BaseModel
from typing import List, Annotated
from analyzer import FileAnalyzer
from file_reader import FileReader
from services.employee_service import EmployeeService
from services.shift_service import ShiftService
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI(title="My Employee Scheduling API")
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/department", tags=["Department"])
async def get_all_departments(db: db_dependency):
    result = db.query(models.DepartmentDB).all()
    return result


@app.get("/department/{id}", tags=["Department"], response_model=models.DepartmentModel)
async def get_department(id: int, db: db_dependency):
    result = db.query(models.DepartmentDB).filter(models.DepartmentDB.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Department not found")
    return result


@app.get("/employee", tags=["Employee"])
async def get_all_employees(db: db_dependency):
    employee_service = EmployeeService(db)
    return employee_service.get_all()


@app.get("/employee/{id}", tags=["Employee"])
async def get_employee(id: int, db: db_dependency):
    result = db.query(models.EmployeeDB).filter(models.EmployeeDB.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result


@app.get("/shift", tags=["Shift"])
async def get_all_shifts(db: db_dependency):
    result = db.query(models.Shift2DB).all()
    return result


@app.get("/shift/{id}", tags=["Shift"])
async def get_shift(id: int, db: db_dependency):
    result = db.query(models.Shift2DB).filter(models.Shift2DB.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Shift not found")
    return result


@app.post("/department", tags=["Department"], status_code=201)
async def create_department(department: models.DepartmentModel, db: db_dependency):
    db_department = models.DepartmentDB(name=department.name)
    db.add(db_department)
    db.commit()
    db.refresh(db_department)


@app.post("/employee", tags=["Employee"], status_code=201)
async def create_employee(employee: models.EmployeeModel, db: db_dependency):
    db_employee = models.EmployeeDB(
        name=employee.name,
        surname=employee.surname,
        code=employee.code,
        active=employee.active,
        department_id=1,
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)


@app.post("/employee2", tags=["Employee"], status_code=201)
async def create_employee(employee_data: models.EmployeeCreate, db: db_dependency):
    employee_service = EmployeeService(db)
    result = employee_service.create(employee_data)
    print("creado: " + str(result.id))


@app.post("/shift", tags=["Shift"], status_code=201)
async def create_shift(shift: models.ShiftModel, db: db_dependency):
    db_shift = models.Shift2DB(
        employee_id=shift.employee_id,
        start_time=shift.start_time,
        end_time=shift.end_time,
        date=shift.date,
        is_holiday=shift.is_holiday,
    )
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)


@app.post("file/analyze")
async def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        filename = file.filename
        """ with open(file.filename, 'wb') as f:
            f.write(contents) """
        open("/tmp/%s" % filename, "wb").write(contents)
        analyzer = FileAnalyzer()
        respuesta, response = analyzer.contar_horas_trabajo("/tmp/", filename)
        errors = []
        if response["hasErrors"]:
            errors.append("Se encontró algún error en los horarios")
        response_data = {"data": response, "errors": errors}
        response_string = json.dumps(response_data)
        print("RESPONSE")
        print(response_string)
        return response_data
    except Exception as errMsg:
        print("ERROR")
        print(errMsg)
        return {"message": "There was an error uploading the file"}


@app.post("/upload")
async def upload(db: db_dependency, file: UploadFile = File(...)):
    try:
        employee_service = EmployeeService(db)
        shift_service = ShiftService(db)
        contents = file.file.read()
        filename = file.filename
        open("/tmp/%s" % filename, "wb").write(contents)
        fr = FileReader()
        fr.read("/tmp/", filename, employee_service, shift_service)
        return {"data": "ok"}
    except Exception as errMsg:
        print("ERROR")
        print(errMsg)
        return {"message": "There was an error uploading the file"}


# Pydantic model for input data
class ShiftCreate(BaseModel):
    date: str
    employee_id: int
    hours: int


# POST method to create a new Shift object
""" @app.post("/testt")
def create_shift(shift_data: ShiftCreate):
    db = SessionLocal()
    shift_data_dict = shift_data.dict()

    # Create a new Shift object
    new_shift = models.TestObjDB(**shift_data_dict)

    # Add the new object to the session and commit the transaction
    db.add(new_shift)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Shift already exists")

    return new_shift """


@app.post("/testt", tags=["Testt"], status_code=201)
async def create_shift(shift_data: ShiftCreate, db: db_dependency):
    shift_data_dict = shift_data.dict()
    db_shift = models.TestObjDB(**shift_data_dict)
    db.merge(db_shift)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Shift already exists")
    return db_shift


""" @app.post("file/analyze")
async def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        filename = file.filename
        open("/tmp/%s" % filename, "wb").write(contents)
        analyzer = FileAnalyzer()
        respuesta, response = analyzer.contar_horas_trabajo("/tmp/", filename)
        errors = []
        if response["hasErrors"]:
            errors.append("Se encontró algún error en los horarios")
        response_data = {"data": response, "errors": errors}
        response_string = json.dumps(response_data)
        print("RESPONSE")
        print(response_string)
        return response_data
    except Exception as errMsg:
        print("ERROR")
        print(errMsg)
        return {"message": "There was an error uploading the file"} """
