from datetime import datetime, timedelta
import calendar
from fastapi import HTTPException
from psycopg2 import IntegrityError
from models import (
    ShiftCreate,
    ShiftCreateObj,
    ShiftDB,
    ShiftDBObj,
    MultipleShiftCreate,
    MultipleShiftCreateObj,
)
from sqlalchemy.orm import joinedload


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

    def createObj(self, shift_data: ShiftCreateObj):
        shift_data_dict = shift_data.dict()
        db_shift = ShiftDBObj(**shift_data_dict)
        self.db.add(db_shift)
        try:
            # Flush the session to ensure the ID is generated
            self.db.flush()
            self.db.commit()
        except IntegrityError as e:
            print("Error creating: " + str(e))
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Shift already exists")
        return db_shift

    def updateObj(self, id: int, shift_update: ShiftCreateObj):
        db_shift = self.db.query(ShiftDBObj).filter(ShiftDBObj.id == id).first()
        if db_shift is None:
            raise HTTPException(status_code=404, detail="Shift not found")

        # Update the fields of the shift
        for key, value in shift_update.dict(exclude_unset=True).items():
            setattr(db_shift, key, value)

        try:
            self.db.commit()
            self.db.refresh(db_shift)
        except IntegrityError as e:
            print("Error updating: " + str(e))
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Error updatinf shift")
        return db_shift

    def create_multiple(self, data: MultipleShiftCreate):
        response = []
        shifts = data.shifts
        for shift in shifts:
            try:
                result = self.create(shift)
                response.append(result)
            except Exception as error:
                print(str(error))
                # create field in shift to store error, for now it is set type=3 to indicate error
                shift.type = 3
                response.append(shift)
        return response

    def create_multiple_obj(self, data: MultipleShiftCreateObj):
        response = []
        shifts = data.shifts
        for shift in shifts:
            try:
                result = self.createObj(shift)
                response.append(result)
            except Exception as error:
                print(str(error))
                # create field in shift to store error, for now it is set type=3 to indicate error
                shift.type = 3
                response.append(shift)
        return response

    def delete_obj(self, id: int):
        db_shift = self.db.query(ShiftDBObj).filter(ShiftDBObj.id == id).first()
        if db_shift is None:
            raise HTTPException(status_code=404, detail="Shift not found")

        try:
            self.db.delete(db_shift)
            self.db.commit()
        except Exception as error:
            print("Error deleting: " + str(error))
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Shift couldn't be deleted")
        return {"message": "Shift deleted successfully"}

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

    def get_all_obj(self, date: datetime = None):
        if date:
            start, end = self.get_month_boundaries(date)
            return (
                self.db.query(ShiftDBObj)
                .filter(ShiftDBObj.start_date >= start, ShiftDBObj.end_date <= end)
                .all()
            )
        return self.db.query(ShiftDBObj).options(joinedload(ShiftDBObj.employee)).all()

    # Mejorar esto si no ecuentra shift, errores, etc
    def get_obj(self, id: int):
        response = self.db.query(ShiftDBObj).filter(ShiftDBObj.id == id).first()
        return response

    def _get_week_range(self, date_str: str):
        date = datetime.strptime(date_str, "%Y-%m-%d")
        start_of_week = date - timedelta(days=date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        start = start_of_week.strftime("%Y-%m-%d")
        end = end_of_week.strftime("%Y-%m-%d")
        return start, end

    def get_week_boundaries(self, dt: datetime):
        # Calculate the start of the week (Monday)
        start_of_week = dt - timedelta(days=dt.weekday())
        start_of_week = datetime.combine(start_of_week, datetime.min.time())

        # Calculate the end of the week (Sunday)
        end_of_week = start_of_week + timedelta(days=6)
        end_of_week = datetime.combine(end_of_week, datetime.max.time())
        print(f"start_of_week: ${start_of_week}")
        print(f"end_of_week: ${end_of_week}")
        return start_of_week, end_of_week

    def get_month_boundaries(self, date: datetime):
        # Get the first day of the month at 00:00
        first_day = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculate the last day of the month at 23:59
        last_day = date.replace(
            day=calendar.monthrange(date.year, date.month)[1], hour=23, minute=59
        )

        return first_day, last_day
