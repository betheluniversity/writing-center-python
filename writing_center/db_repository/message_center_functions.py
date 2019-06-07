from datetime import datetime, timedelta
from sqlalchemy import orm
from flask import session as flask_session
from writing_center.db_repository import db_session
from writing_center.db_repository.tables import WCEmailPreferencesTable, WCAppointmentDataTable, WCDropInAppointmentsTable


class Message_Center:
    def get_email_preferences(self, user_id):
        return (db_session.query(WCEmailPreferencesTable)
                .filter(WCEmailPreferencesTable.id == user_id)
                .all())

    def change_email_preferences(self, substitute, shift, user_id):
        row = self.get_email_preferences(user_id)
        row.SubRequestEmail = substitute
        row.StudentSignupEmail = shift
        db_session.commit()

    def get_appointment_info(self, appointment_id):
        pass


