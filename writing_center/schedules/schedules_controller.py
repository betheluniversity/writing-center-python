from sqlalchemy import orm
from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, UserRoleTable, RoleTable, WCScheduleTable


class SchedulesController:
    def __init__(self):
        pass

    def get_schedules(self):
        return db_session.query(WCScheduleTable)\
            .all()

    def create_schedule(self, start_time, end_time, is_active):
        # TODO ADD CHECK FOR EXISTING SCHEDULES
        new_schedule = WCScheduleTable(timeStart=start_time, timeEnd=end_time, isActive=is_active)
        db_session.add(new_schedule)
        db_session.commit()

    def check_for_existing_schedule(self, start_time, end_time):
        try:  # return true if there is an existing user
            schedule = db_session.query(WCScheduleTable)\
                .filter(WCScheduleTable.timeStart == start_time)\
                .filter(WCScheduleTable.timeEnd == end_time)\
                .one()
            return True
        except orm.exc.NoResultFound:  # otherwise return false
            return False

    def get_tutors(self):
        return db_session.query(UserTable)\
            .filter(UserTable.id == UserRoleTable.user_id)\
            .filter(UserRoleTable.role_id == RoleTable.id)\
            .filter(RoleTable.role == 'role_tutor')\
            .all()
