from datetime import datetime, timedelta

from writing_center.db_repository import db_session
from writing_center.db_repository.tables import AppointmentsTable, UserTable


class CronController:
    def __init__(self):
        pass

    def get_upcoming_appointments(self):
        tomorrow = datetime.now() + timedelta(days=1)
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.student_id != None)\
            .filter(AppointmentsTable.scheduledStart > tomorrow)\
            .filter(AppointmentsTable.scheduledStart < tomorrow + timedelta(days=1))\
            .all()

    def get_user(self, user_id):
        return db_session.query(UserTable).filter(UserTable.id == user_id).one()
