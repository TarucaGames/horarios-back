from models import EmployeeCreate, EmployeeDB, EmployeeUpdate
from fastapi import HTTPException


class EmployeeService:
    def __init__(self, db) -> None:
        self.db = db

    def get_all(self):
        return (
            self.db.query(EmployeeDB)
            .order_by(EmployeeDB.active.desc(), EmployeeDB.id)
            .all()
        )

    def get(self, id):
        return self.db.query(EmployeeDB).filter(EmployeeDB.id == id).first()

    def create(self, employee_data: EmployeeCreate):
        employee_data_dict = employee_data.dict()
        db_employee = EmployeeDB(**employee_data_dict)
        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)
        return db_employee

    def update(self, id: int, employee_data: EmployeeUpdate):
        employee = self.db.query(EmployeeDB).filter(EmployeeDB.id == id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        try:
            for key, value in vars(employee_data).items():
                if value is not None:
                    setattr(employee, key, value)
            self.db.commit()
            self.db.refresh(employee)
            return employee
        except Exception as error:
            print("Error uploading employee: " + str(error))
            raise HTTPException(status_code=400, detail="Employee couldn't be updated")

    def delete(self, id: int):
        employee = self.db.query(EmployeeDB).filter(EmployeeDB.id == id).first()
        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")

        try:
            self.db.delete(employee)
            self.db.commit()
        except Exception as error:
            print("Error deleting: " + str(error))
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Employee couldn't be deleted")
        return {"message": "Employee deleted successfully"}
