from datetime import datetime, timedelta
from flask import session as flask_session

from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, AppointmentsTable, SettingsTable, UserRoleTable, RoleTable


class AppointmentsController:
    def __init__(self):
        pass

    def get_user_by_username(self, username):
        return db_session.query(UserTable)\
            .filter(UserTable.username == username)\
            .one_or_none()

    def get_user_by_id(self, user_id):
        return db_session.query(UserTable)\
            .filter(UserTable.id == user_id)\
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

    def get_users_by_role(self, role_name):
        return db_session.query(UserTable)\
            .filter(UserTable.id == UserRoleTable.user_id)\
            .filter(UserRoleTable.role_id == RoleTable.id)\
            .filter(RoleTable.name == role_name)\
            .order_by(UserTable.lastName).all()

    def get_profs(self):
        profs = db_session.query(AppointmentsTable.profName)\
            .filter(AppointmentsTable.profName != None)\
            .order_by(AppointmentsTable.profName)\
            .distinct()
        prof_list = []
        for prof in profs:
            prof_name = str(prof).split('\'')
            prof_list.append(prof_name[1])
        return prof_list


    def get_courses(self):
        courses = db_session.query(AppointmentsTable.courseCode)\
            .filter(AppointmentsTable.courseCode != None)\
            .order_by(AppointmentsTable.courseCode)\
            .distinct()
        course_list = []
        for course in courses:
            course_code = str(course).split('\'')
            course_list.append(course_code[1])
        return course_list

    def search_appointments(self, student, tutor, prof, course, start, end):
        appts = db_session.query(AppointmentsTable)
        if student:
             appts = appts.filter(AppointmentsTable.student_id == student)
        if tutor:
            appts = appts.filter(AppointmentsTable.tutor_id == tutor)
        if prof:
            appts = appts.filter(AppointmentsTable.profName == prof)
        if course:
            if len(course) > 1:
                appts = appts.filter(AppointmentsTable.courseCode == course)
            else:
                appts = appts.filter(AppointmentsTable.courseCode.like("____%{0}%".format(course)))
        if start:
            appts = appts.filter(AppointmentsTable.scheduledStart > start)
        if end:
            appts = appts.filter(AppointmentsTable.scheduledEnd < end)
        return appts.order_by(AppointmentsTable.scheduledStart.desc()).all()
