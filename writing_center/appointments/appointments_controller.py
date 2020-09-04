from datetime import datetime, timedelta
from flask import session as flask_session
from sqlalchemy import or_

from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, AppointmentsTable, SettingsTable, UserRoleTable, RoleTable


class AppointmentsController:
    def __init__(self):
        pass

    def check_for_existing_user(self, username):
        try:
            user = db_session.query(UserTable)\
                .filter(UserTable.username == username)\
                .one_or_none()
            if user.bannedDate != None:
                self.reactivate_user(user.id)
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

    def schedule_appointment(self, appt_id, course, assignment):
            appointment = db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.id == appt_id)\
                .one_or_none()

            appointment.profName = None
            appointment.profEmail = None
            appointment.assignment = None
            appointment.notes = None
            appointment.suggestions = None
            appointment.courseCode = None
            appointment.courseSection = None
            appointment.noShow = 0

            # Updates the student username
            user = self.get_user_by_username(flask_session['USERNAME'])
            appointment.student_id = user.id
            appointment.assignment = assignment.encode('latin-1', 'ignore')  # this ignores invalid characters
            if course:
                appointment.courseCode = course['course_code']
                appointment.courseSection = course['section']
                appointment.profName = course['instructor']
                appointment.profEmail = course['instructor_email']
            # Commits to DB
            try:
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
            appointment.profName = None
            appointment.profEmail = None
            appointment.assignment = None
            appointment.courseCode = None
            appointment.courseSection = None
            db_session.commit()
            return True
        except Exception as e:
            return False

    def begin_walk_in_appointment(self, user, tutor, course, assignment, multilingual):
        if course:
            course_code = course['course_code']
            course_section = course['section']
            prof_name = course['instructor']
            prof_email = course['instructor_email']
            begin_appt = AppointmentsTable(student_id=user.id, tutor_id=tutor.id,
                                           actualStart=datetime.now(), profName=prof_name, profEmail=prof_email,
                                           assignment=assignment, courseCode=course_code, courseSection=course_section,
                                           inProgress=1, dropIn=1, sub=0, multilingual=multilingual, noShow=0)
        else:
            begin_appt = AppointmentsTable(student_id=user.id, tutor_id=tutor.id,
                                           actualStart=datetime.now(), assignment=assignment, inProgress=1, dropIn=1,
                                           sub=0, multilingual=multilingual, noShow=0)
        db_session.add(begin_appt)
        try:
            db_session.commit()
            return begin_appt
        except Exception as e:
            return False

    def get_scheduled_appointments(self, username):
        tutor = self.get_user_by_username(username)
        min_today = datetime.combine(datetime.now(), datetime.min.time())
        max_today = datetime.combine(datetime.now(), datetime.max.time())
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.scheduledStart >= min_today)\
            .filter(AppointmentsTable.scheduledEnd <= max_today)\
            .filter(AppointmentsTable.student_id != None)\
            .filter(AppointmentsTable.tutor_id == tutor.id)\
            .all()

    def get_in_progress_appointments(self, username):
        tutor = self.get_user_by_username(username)
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.scheduledStart != None)\
            .filter(AppointmentsTable.scheduledEnd == None)\
            .filter(AppointmentsTable.student_id != None)\
            .filter(AppointmentsTable.tutor_id == tutor.id)\
            .all()

    def get_in_progress_walk_ins(self, username):
        tutor = self.get_user_by_username(username)
        min_today = datetime.combine(datetime.now(), datetime.min.time())
        max_today = datetime.combine(datetime.now(), datetime.max.time())
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.actualStart >= min_today)\
            .filter(or_(AppointmentsTable.actualEnd == None, AppointmentsTable.actualEnd <= max_today))\
            .filter(AppointmentsTable.student_id != None)\
            .filter(AppointmentsTable.tutor_id == tutor.id)\
            .all()

    def tutor_change_appt(self, appt_id, assignment, notes, suggestions):
        try:
            appt = self.get_appointment_by_id(appt_id)
            appt.assignment = assignment
            appt.notes = notes
            appt.suggestions = suggestions
            db_session.commit()
            return True
        except Exception as e:
            return False

    def mark_no_show(self, appt_id):
        appointment = db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.id == appt_id)\
            .one_or_none()
        appointment.noShow = 1
        db_session.commit()

    def revert_no_show(self, appt_id):
        appointment = db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.id == appt_id)\
            .one_or_none()
        appointment.noShow = 0
        db_session.commit()

    def mark_multilingual(self, appt_id):
        appointment = db_session.query(AppointmentsTable).filter(AppointmentsTable.id == appt_id).one_or_none()
        appointment.multilingual = 1
        db_session.commit()

    def revert_multilingual(self, appt_id):
        appointment = db_session.query(AppointmentsTable).filter(AppointmentsTable.id == appt_id).one_or_none()
        appointment.multilingual = 0
        db_session.commit()

    def ban_if_no_show_check(self, user_id):
        no_show_count = db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.student_id == user_id)\
            .filter(AppointmentsTable.noShow == 1)\
            .count()
        if no_show_count > int(self.get_ban_limit()[0]):
            self.ban_user(user_id)

    def ban_user(self, user_id):
        user = self.get_user_by_id(user_id)
        user.bannedDate = datetime.now()
        db_session.commit()

    def start_appointment(self, appt_id):
        appointment = db_session.query(AppointmentsTable) \
            .filter(AppointmentsTable.id == appt_id) \
            .one_or_none()
        appointment.inProgress = 1
        appointment.actualStart = datetime.now()
        db_session.commit()

    def end_appointment(self, appt_id, course, assignment, notes, suggestions):
        appointment = db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.id == appt_id)\
            .one_or_none()
        appointment.inProgress = 0
        if not course:
            appointment.courseCode = None
            appointment.courseSection = None
            appointment.profName = None
            appointment.profEmail = None
        else:
            appointment.courseCode = course['course_code']
            appointment.courseSection = course['section']
            appointment.profName = course['instructor']
            appointment.profEmail = course['instructor_email']
        appointment.assignment = assignment
        appointment.notes = notes
        appointment.suggestions = suggestions
        appointment.actualEnd = datetime.now()

        db_session.commit()

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

    def get_walk_in_appointments_in_range(self, start, end):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.actualStart >= start)\
            .filter(AppointmentsTable.actualEnd <= end)\
            .filter(AppointmentsTable.tutor_id != None)\
            .all()

    def get_open_appointments_in_range(self, start, end, time_limit):
        time_limit = datetime.now() + timedelta(minutes=time_limit)
        return db_session.query(AppointmentsTable) \
            .filter(AppointmentsTable.scheduledStart >= start)\
            .filter(AppointmentsTable.scheduledStart >= time_limit)\
            .filter(AppointmentsTable.scheduledEnd <= end)\
            .filter(AppointmentsTable.tutor_id != None)\
            .filter(AppointmentsTable.student_id == None)\
            .all()

    def get_no_show_appointments_in_range(self, start, end, time_limit):
            time_limit = datetime.now() + timedelta(minutes=time_limit)
            return db_session.query(AppointmentsTable) \
                .filter(AppointmentsTable.scheduledStart >= start) \
                .filter(AppointmentsTable.scheduledStart >= time_limit) \
                .filter(AppointmentsTable.scheduledEnd <= end) \
                .filter(AppointmentsTable.tutor_id != None) \
                .filter(AppointmentsTable.student_id != None) \
                .filter(AppointmentsTable.noShow) \
                .all()

    def get_future_user_appointments(self, user_id):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.student_id == user_id)\
            .filter(AppointmentsTable.scheduledStart > datetime.now())\
            .all()

    def get_weekly_users_appointments(self, user_id, start_date):
        if start_date.weekday() != 6:
            while start_date.weekday() != 6:
                start_date += timedelta(days=-1)

        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = start_date + timedelta(days=6)
        end_date = datetime.combine(end_date, datetime.max.time())

        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.student_id == user_id)\
            .filter(AppointmentsTable.scheduledStart >= start_date)\
            .filter(AppointmentsTable.scheduledEnd <= end_date)\
            .all()

    def get_appointment_limit(self):
        return db_session.query(SettingsTable.value)\
            .filter(SettingsTable.id == 1)\
            .one_or_none()

    def get_time_limit(self):
        return db_session.query(SettingsTable.value)\
            .filter(SettingsTable.id == 2)\
            .one_or_none()

    def get_ban_limit(self):
        return db_session.query(SettingsTable.value)\
            .filter(SettingsTable.id == 3)\
            .one_or_none()

    def get_survey_link(self):
        return db_session.query(SettingsTable.value)\
            .filter(SettingsTable.id == 4)\
            .one_or_none()

    def get_zoom_url(self):
        return db_session.query(SettingsTable.value)\
            .filter(SettingsTable.id == 5)\
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

    def get_profs_and_emails(self):
        profs = db_session.query(AppointmentsTable.profName, AppointmentsTable.profEmail) \
            .filter(AppointmentsTable.profName != None) \
            .order_by(AppointmentsTable.profName) \
            .distinct()
        profs_and_emails = {}
        for prof in profs:
            # prof_name = str(prof.profName).split('\'')
            profs_and_emails[prof.profName] = prof.profEmail
        return profs_and_emails

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

    def get_all_users(self):
        return db_session.query(UserTable).all()

    def search_appointments(self, student, tutor, prof, course, start, end):
        appts = db_session.query(AppointmentsTable)
        if student:
             appts = appts.filter(AppointmentsTable.student_id == student)
        if tutor:
            appts = appts.filter(AppointmentsTable.tutor_id == tutor)
        if prof:
            appts = appts.filter(AppointmentsTable.profName == prof)
        if course:  # This can be a courseCode or a tag so handle both here
            if len(course) > 1:
                appts = appts.filter(AppointmentsTable.courseCode == course)
            else:
                appts = appts.filter(AppointmentsTable.courseCode.like("____%{0}%".format(course)))
        if start:
            appts = appts.filter(AppointmentsTable.actualStart > start)
        if end:
            appts = appts.filter(AppointmentsTable.actualEnd < end)
        return appts.order_by(AppointmentsTable.scheduledStart.desc()).all()

    def edit_appt(self, appt_id, student_id, tutor_id, sched_start, sched_end, actual_start, actual_end, prof_name,
                  prof_email, drop_in, virtual, sub, assignment, notes, suggestions, multiligual, course, section, no_show,
                  in_progress):
        appt = db_session.query(AppointmentsTable).filter(AppointmentsTable.id == appt_id).one()
        appt.student_id = student_id
        appt.tutor_id = tutor_id
        appt.scheduledStart = sched_start
        appt.scheduledEnd = sched_end
        appt.actualStart = actual_start
        appt.actualEnd = actual_end
        appt.profName = prof_name
        appt.profEmail = prof_email
        appt.dropIn = drop_in
        appt.online = virtual
        appt.sub = sub
        appt.assignment = assignment
        appt.notes = notes
        appt.suggestions = suggestions
        appt.multilingual = multiligual
        appt.courseCode = course
        appt.courseSection = section
        appt.noShow = no_show
        appt.inProgress = in_progress
        db_session.commit()
