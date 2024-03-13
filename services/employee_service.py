import models


class EmployeeService:
    def __init__(self, db) -> None:
        self.db = db

    def create(self, employee_data: models.EmployeeCreate):
        employee_data_dict = employee_data.dict()
        db_employee = models.EmployeeDB(**employee_data_dict)
        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)
        return db_employee

    def get_all(self):
        return self.db.query(models.EmployeeDB).all()
