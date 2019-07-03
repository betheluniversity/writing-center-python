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

    def get_filled_appointments(self):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.student_id != None)\
            .all()

    def get_yearly_appointments(self, selected_year):
        yearly_appts = db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.student_id != None)\
            .all()
        appts_list = []
        for appts in yearly_appts:
            if int(appts.scheduledStart.strftime('%Y')) == selected_year:
                appts_list.append(appts)
        return appts_list

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

    def get_all_open_appointments(self):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.student_id == None)\
            .filter(AppointmentsTable.scheduledStart > datetime.now())\
            .all()

    def create_appointment(self, id, start_time, end_time):
        appointment = db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.id == id)\
            .one_or_none()
        # Formats the time to fit the DB's format
        start_time = start_time.replace("T", " ")
        start_time = start_time.replace(".000Z", "")
        end_time = end_time.replace("T", " ")
        end_time = end_time.replace(".000Z", "")
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        # Updates the start time, end time, and student username
        appointment.scheduledStart = start_time
        appointment.scheduledEnd = end_time
        user = self.get_user_by_username(flask_session['USERNAME'])
        appointment.student_id = user.id
        # Commits to DB
        db_session.commit()
        if appointment:
            return True
        else:
            return False

    def get_user_info(self, user_id):
        return db_session.query(UserTable)\
            .filter(UserTable.id == user_id)\
            .one_or_none()
