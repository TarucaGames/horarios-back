from fastapi import HTTPException
from psycopg2 import IntegrityError
from models import ShiftCreate, ShiftDB


class ShiftService:
    def __init__(self, db) -> None:
        self.db = db

    def create(self, shift_data: ShiftCreate):
        shift_data_dict = shift_data.dict()
        db_shift = ShiftDB(**shift_data_dict)
        self.db.merge(db_shift)
        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Shift already exists")
        return db_shift

    def delete(self, week_number: int):
        try:
            self.db.query(ShiftDB).filter(ShiftDB.week == int(week_number)).delete()
            self.db.commit()
        except Exception as error:
            self.db.rollback()
            print(str(error))
            raise HTTPException(status_code=400, detail="Shifts couldn't be deleted")
