from datetime import datetime, timedelta

from writing_center.db_repository import db_session
from writing_center.db_repository.tables import AppointmentsTable, UserTable


class CronController:
    def __init__(self):
        pass

    def get_upcoming_appointments(self):
        now = datetime.now()
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.student_id != None)\
            .filter(AppointmentsTable.scheduledStart > now)\
            .filter(AppointmentsTable.scheduledStart < now + timedelta(days=1))\
            .all()

    def get_student_email(self, student_id):
        return db_session.query(UserTable).filter(UserTable.id == student_id).one()
