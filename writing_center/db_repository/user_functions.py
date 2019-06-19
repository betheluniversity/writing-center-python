from datetime import datetime, timedelta
from sqlalchemy import orm
from flask import session as flask_session
from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, WCAppointmentDataTable, UserRoleTable


class UserFunctions:
    def get_user(self, username):
        return (db_session.query(UserTable)
                .filter(UserTable.username == username)
                .one())

    def get_end_of_session_recipients(self, appointment_id):
        appointment = (db_session.query(WCAppointmentDataTable)
                       .filter(WCAppointmentDataTable.ID == appointment_id)
                       .all())

        recipients = [self.get_user(appointment.ProfUsername), self.get_user(appointment.StudUsername)]
        return recipients

    def get_user_roles(self, user_id):
        return (db_session.query(UserRoleTable)
                .filter(UserRoleTable.user_id == user_id)
                .one())
