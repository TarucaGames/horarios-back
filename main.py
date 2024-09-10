import uvicorn
import json
from fastapi import FastAPI, File, HTTPException, Depends, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from psycopg2 import IntegrityError
from pydantic import BaseModel
from typing import List, Annotated, Optional
from analyzer import FileAnalyzer
from file_reader import FileReader
from services.employee_service import EmployeeService
from services.shift_service import ShiftService
from services.user_service import UserService
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

origins = [
    "http://localhost",
    "https://9000-idx-employee-planner-1717323653464.cluster-rcyheetymngt4qx5fpswua3ry4.cloudworkstations.dev",  # Example for Angular development server
]

app = FastAPI(title="My Employee Scheduling API")
# Add CORS middleware with appropriate configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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


@app.get("/shift", tags=["Shift"])
async def get_all_shifts(db: db_dependency, date: Optional[str] = Query(None)):
    shift_service = ShiftService(db)
    return shift_service.get_all(date)


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


##############################
##### EMPLOYEE ENDPOINTS #####
##############################
@app.get("/employee", tags=["Employee"], response_model=List[models.EmployeeResponse])
async def get_all_employees(db: db_dependency):
    employee_service = EmployeeService(db)
    return employee_service.get_all()


@app.get("/employee/{id}", tags=["Employee"], response_model=models.EmployeeResponse)
async def get_employee(id: int, db: db_dependency):
    employee_service = EmployeeService(db)
    result = employee_service.get(id)
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result


@app.post(
    "/employee",
    tags=["Employee"],
    response_model=models.EmployeeResponse,
    status_code=201,
)
async def create_employee(employee_data: models.EmployeeCreate, db: db_dependency):
    employee_service = EmployeeService(db)
    return employee_service.create(employee_data)


@app.put("/employee/{id}", tags=["Employee"], response_model=models.EmployeeResponse)
async def update_employee(
    id: int, employee_data: models.EmployeeUpdate, db: db_dependency
):
    employee_service = EmployeeService(db)
    return employee_service.update(id, employee_data)


@app.delete("/employee/{id}", tags=["Employee"])
async def delete_shift(db: db_dependency, id: int):
    employee_service = EmployeeService(db)
    return employee_service.delete(id)


##############################
###### SHIFT ENDPOINTS #######
##############################
@app.post("/shift", tags=["Shift"], status_code=201)
async def create_shift(db: db_dependency, shift: models.ShiftCreate):
    shift_service = ShiftService(db)
    return shift_service.create(shift)


@app.get("/shiftobj", tags=["ShiftObj"], response_model=List[models.ShiftResponse])
async def get_all_shifts(db: db_dependency, date: Optional[datetime] = Query(None)):
    shift_service = ShiftService(db)
    return shift_service.get_all_obj(date)


@app.get("/shiftobj/{id}", tags=["ShiftObj"], response_model=models.ShiftResponse)
async def get_shift(db: db_dependency, id: int):
    shift_service = ShiftService(db)
    return shift_service.get_obj(id)


@app.post(
    "/shiftobj", tags=["ShiftObj"], response_model=models.ShiftResponse, status_code=201
)
async def create_shift(db: db_dependency, shift: models.ShiftCreateObj):
    shift_service = ShiftService(db)
    return shift_service.createObj(shift)


@app.put(
    "/shiftobj/{id}",
    tags=["ShiftObj"],
    response_model=models.ShiftResponse,
)
async def create_shift(db: db_dependency, id: int, shift: models.ShiftCreateObj):
    shift_service = ShiftService(db)
    return shift_service.updateObj(id, shift)


@app.post("/shiftobj/multiple", tags=["ShiftObj"], status_code=201)
async def create_shift(db: db_dependency, data: models.MultipleShiftCreateObj):
    shift_service = ShiftService(db)
    return shift_service.create_multiple_obj(data)


@app.delete("/shiftobj/{id}", tags=["ShiftObj"])
async def delete_shift(db: db_dependency, id: int):
    shift_service = ShiftService(db)
    return shift_service.delete_obj(id)


@app.post("/shift/multiple", tags=["Shift"], status_code=201)
async def create_shift(db: db_dependency, data: models.MultipleShiftCreate):
    shift_service = ShiftService(db)
    return shift_service.create_multiple(data)


@app.post("/file/analyze")
async def upload(db: db_dependency, file: UploadFile = File(...)):
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


@app.post("/upload-single")
async def upload(
    db: db_dependency, employee_id: int = Query(None), file: UploadFile = File(...)
):
    try:
        employee_service = EmployeeService(db)
        shift_service = ShiftService(db)
        contents = file.file.read()
        filename = file.filename
        open("/tmp/%s" % filename, "wb").write(contents)
        fr = FileReader()
        response = fr.read_single(
            "/tmp/", filename, employee_service, shift_service, employee_id
        )
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


##############################
##### USERS ENDPOINTS #####
##############################
# Register a new user
@app.post("/register", response_model=models.UserResponse)
def register_user(db: db_dependency, user_data: models.UserCreate):
    user_service = UserService(db)
    return user_service.register_user(user_data)


# Authenticate the user and return a JWT token
@app.post("/token")
async def get_token(
    db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()
):
    user_service = UserService(db)
    return user_service.get_token(form_data)


# Get the current user using the token
@app.get("/users/me", response_model=models.UserResponse)
async def read_users_me(db: db_dependency, token: str = Depends(oauth2_scheme)):
    user_service = UserService(db)
    return user_service.get_current_user(token)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
