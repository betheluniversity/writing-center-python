from datetime import datetime, timedelta
from flask import session as flask_session

from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, AppointmentsTable, SettingsTable, UserRoleTable


class AppointmentsController:
    def __init__(self):
        pass

    def check_for_existing_user(self, username):
        try:
            user = db_session.query(UserTable)\
                .filter(UserTable.username == username)\
                .one_or_none()
            return user
        except Exception as e:
            return False

    def reactivate_user(self, user_id):
        user = db_session.query(UserTable)\
            .filter(UserTable.id == user_id)\
            .one_or_none()
        user.deletedAt = None
        db_session.commit()

    def create_user(self, username, name):
        first_name = name['0']['firstName']
        last_name = name['0']['lastName']
        email = '{0}@bethel.edu'.format(username)
        user = UserTable(username=username, email=email, firstName=first_name, lastName=last_name,)
        db_session.add(user)
        db_session.commit()
        user_role = UserRoleTable(user_id=user.id, role_id=4)
        db_session.add(user_role)
        db_session.commit()

    def get_user_by_username(self, username):
        return db_session.query(UserTable)\
            .filter(UserTable.username == username)\
            .one_or_none()

    def get_user_by_id(self, student_id):
        try:
            return db_session.query(UserTable)\
                .filter(UserTable.id == student_id)\
                .one_or_none()
        except:
            return None

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

    def schedule_appointment(self, appt_id):
        try:
            appointment = db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.id == appt_id)\
                .one_or_none()
            # Updates the student username
            user = self.get_user_by_username(flask_session['USERNAME'])
            appointment.student_id = user.id
            # Commits to DB
            db_session.commit()
            return True
        except Exception as e:
            return False

    def cancel_appointment(self, appt_id):
        try:
            appointment = db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.id == appt_id)\
                .one_or_none()
            appointment.student_id = None
            db_session.commit()
            return True
        except Exception as e:
            return False

    def begin_walk_in_appointment(self, user, tutor, course, assignment):
        if course:
            course_code = course['course_code']
            course_section = course['section']
            prof_name = course['instructor']
            prof_email = course['instructor_email']
            begin_appt = AppointmentsTable(student_id=user.id, tutor_id=tutor.id, scheduledStart=datetime.now(),
                                           actualStart=datetime.now(), profName=prof_name, profEmail=prof_email,
                                           assignment=assignment, courseCode=course_code, courseSection=course_section,
                                           inProgress=1)
        else:
            begin_appt = AppointmentsTable(student_id=user.id, tutor_id=tutor.id, scheduledStart=datetime.now(),
                                           actualStart=datetime.now(), assignment=assignment, inProgress=1)
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

    def revert_no_show(self, appt_id):
        try:
            appointment = db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.id == appt_id)\
                .one_or_none()
            appointment.noShow = 0
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
            if not appointment.scheduledEnd:
                appointment.scheduledEnd = datetime.now()
            db_session.commit()
            return True
        except Exception as e:
            return False

    def get_appointment_by_id(self, appt_id):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.id == appt_id)\
            .one_or_none()

    def get_appointments_in_range(self, start, end):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.scheduledStart >= start)\
            .filter(AppointmentsTable.scheduledEnd <= end)\
            .filter(AppointmentsTable.tutor_id != None)\
            .all()

    def get_open_appointments_in_range(self, start, end, time_limit):
        time_limit = datetime.now() + timedelta(hours=time_limit)
        return db_session.query(AppointmentsTable) \
            .filter(AppointmentsTable.scheduledStart >= time_limit)\
            .filter(AppointmentsTable.scheduledStart >= start)\
            .filter(AppointmentsTable.scheduledEnd <= end)\
            .filter(AppointmentsTable.tutor_id != None)\
            .filter(AppointmentsTable.student_id == None)\
            .all()

    def get_one_appointment(self, appt_id):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.id == appt_id)\
            .one_or_none()

    def get_future_user_appointments(self, user_id):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.student_id == user_id)\
            .filter(AppointmentsTable.scheduledStart > datetime.now())\
            .all()

    def get_appointment_limit(self):
        return db_session.query(SettingsTable.value)\
            .filter(SettingsTable.id == 1)\
            .one_or_none()

    def get_time_limit(self):
        return db_session.query(SettingsTable.value)\
            .filter(SettingsTable.id == 2)\
            .one_or_none()
