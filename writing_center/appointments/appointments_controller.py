from datetime import datetime
from flask import session as flask_session

from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, AppointmentsTable


class AppointmentsController:
    def __init__(self):
        pass

    def get_user_by_username(self, username):
        return db_session.query(UserTable)\
            .filter(UserTable.username == username)\
            .one_or_none()

    def get_user_by_id(self, student_id):
        return db_session.query(UserTable)\
            .filter(UserTable.id == student_id)\
            .one_or_none()

    def get_user_by_appt(self, appt_id):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.id == appt_id)\
            .one_or_none()

    def get_all_user_appointments(self, username):
        user = self.get_user_by_username(username)
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.student_id == user.id)\
            .all()

    def get_years(self):
        years = [2014]
        year = 2015
        current_year = datetime.now()
        current_year = int(current_year.strftime('%Y'))
        while year <= current_year:
            years.append(year)
            year += 1
        return years

    def create_appointment(self, appt_id):
        appointment = db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.id == appt_id)\
            .one_or_none()
        # Updates the student username
        user = self.get_user_by_username(flask_session['USERNAME'])
        appointment.student_id = user.id
        # Commits to DB
        db_session.commit()
        if appointment:
            return True
        else:
            return False

    def begin_appointment(self, username):
        user = self.get_user_by_username(username)
        begin_appt = AppointmentsTable(student_id=user.id, actualStart=datetime.now(), inProgress=1)
        db_session.add(begin_appt)
        db_session.commit()

    def get_scheduled_appointments(self, username):
        tutor = self.get_user_by_username(username)
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.tutor_id == tutor.id)\
            .all()

    def mark_no_show(self, appt_id):
        try:
            appointment = db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.id == appt_id)\
                .one_or_none()
            appointment.noShow = 1
            db_session.commit()
            return True
        except Exception as e:
            return False

    def continue_appointment(self, appt_id):
        try:
            appointment = db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.id == appt_id)\
                .one_or_none()
            appointment.inProgress = 1
            appointment.actualEnd = None
            db_session.commit()
            return True
        except Exception as e:
            return False

    def start_appointment(self, appt_id):
        try:
            appointment = db_session.query(AppointmentsTable) \
                .filter(AppointmentsTable.id == appt_id) \
                .one_or_none()
            appointment.inProgress = 1
            appointment.actualStart = datetime.now()
            db_session.commit()
            return True
        except Exception as e:
            return False

    def end_appointment(self, appt_id):
        try:
            appointment = db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.id == appt_id)\
                .one_or_none()
            appointment.inProgress = 0
            appointment.actualEnd = datetime.now()
            db_session.commit()
            return True
        except Exception as e:
            return False

    def get_appointments_in_range(self, start, end):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.scheduledStart >= start)\
            .filter(AppointmentsTable.scheduledEnd <= end)\
            .filter(AppointmentsTable.tutor_id != None)\
            .all()

    def get_open_appointments_in_range(self, start, end):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.scheduledStart >= start)\
            .filter(AppointmentsTable.scheduledEnd <= end)\
            .filter(AppointmentsTable.tutor_id != None)\
            .filter(AppointmentsTable.student_id == None)\
            .all()

    def get_one_appointment(self, appt_id):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.id == appt_id)\
            .one_or_none()
