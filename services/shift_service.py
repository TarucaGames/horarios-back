from datetime import datetime, timedelta
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

    def get_all(self, date: str = None):
        if date:
            start, end = self._get_week_range(date)
            return (
                self.db.query(ShiftDB)
                .filter(ShiftDB.date >= start, ShiftDB.end_time <= end)
                .all()
            )
        return self.db.query(ShiftDB).all()

    def _get_week_range(self, date_str: str):
        date = datetime.strptime(date_str, "%Y-%m-%d")
        start_of_week = date - timedelta(days=date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        start = start_of_week.strftime("%Y-%m-%d")
        end = end_of_week.strftime("%Y-%m-%d")
        return start, end
