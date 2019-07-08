from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, AppointmentsTable


class StatisticsController:
    def __init__(self):
        pass

    def get_user_by_username(self, username):
        return db_session.query(UserTable)\
            .filter(UserTable.username == username)\
            .one_or_none()

    def get_appt_hours(self, start, end, username):
        user = self.get_user_by_username(username)
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.tutor_id == user.id)\
            .filter(AppointmentsTable.actualStart >= start)\
            .filter(AppointmentsTable.actualEnd <= end)\
            .all()