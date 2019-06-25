from datetime import datetime, timedelta
from sqlalchemy import orm
from flask import session as flask_session
from writing_center.db_repository import db_session
from writing_center.db_repository.tables import WCEmailPreferencesTable, WCAppointmentDataTable, WCDropInAppointmentsTable, RoleTable


class MessageCenter:
    def get_email_preferences(self, user_id):
        return (db_session.query(WCEmailPreferencesTable)
                .filter(WCEmailPreferencesTable.id == user_id)
                .one())

    def change_email_preferences(self, substitute, shift, user_id):
        user = self.get_email_preferences(user_id)
        user.SubRequestEmail = substitute
        user.StudentSignUpEmail = shift
        db_session.commit()

    def get_appointment_info(self, appointment_id):
        return (db_session.query(WCAppointmentDataTable)
                .filter(WCAppointmentDataTable.ID == appointment_id)
                .one())

    def get_substitute_email_recipients(self):
        return (db_session.query(WCEmailPreferencesTable, RoleTable)
                .filter(WCEmailPreferencesTable.SubRequestEmail == 1)
                .filter(RoleTable.role == 'Admin')
                .all())

    def get_shift_email_recipients(self):
        """This method is going to select the tutor who's ID matches the ID of the appointment the student signed up for
        then, it will check if that tutor has the StudentSignUpEmail enabled. After that, it will grab all writing
        center admin and return that list as recipients"""
