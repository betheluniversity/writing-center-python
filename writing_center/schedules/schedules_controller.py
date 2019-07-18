from sqlalchemy import orm
from datetime import datetime, timedelta, date


from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, UserRoleTable, RoleTable, ScheduleTable, AppointmentsTable, \
    SettingsTable


class SchedulesController:
    def __init__(self):
        pass

    def get_schedules(self):
        return db_session.query(ScheduleTable).all()

    def create_schedule(self, start_time, end_time, is_active):
        try:
            if self.check_for_existing_schedule(start_time, end_time):
                return False
            new_schedule = ScheduleTable(startTime=start_time, endTime=end_time, active=is_active)
            db_session.add(new_schedule)
            db_session.commit()
            return True
        except Exception as e:
            return False

    def check_for_existing_schedule(self, start_time, end_time):
        try:
            schedule = db_session.query(ScheduleTable)\
                .filter(ScheduleTable.startTime == start_time)\
                .filter(ScheduleTable.endTime == end_time)\
                .one()
            return True
        except orm.exc.NoResultFound:  # otherwise return false
            return False

    def get_user_by_name(self, first_name, last_name):
        return db_session.query(UserTable)\
            .filter(UserTable.firstName == first_name)\
            .filter(UserTable.lastName == last_name)\
            .one_or_none()

    def get_user_by_username(self, username):
        return db_session.query(UserTable)\
            .filter(UserTable.username == username)\
            .one_or_none()

    def get_user_by_id(self, id):
        return db_session.query(UserTable)\
            .filter(UserTable.id == id)\
            .one_or_none()

    def get_tutors(self):
        return db_session.query(UserTable)\
            .filter(UserTable.id == UserRoleTable.user_id)\
            .filter(UserRoleTable.role_id == RoleTable.id)\
            .filter(RoleTable.name == 'Tutor')\
            .all()

    def create_tutor_shifts(self, start_date, end_date, multilingual, drop_in, tutor_names, days_of_week, time_slots):
        if multilingual == "Yes":
            multilingual = 1
        else:
            multilingual = 0

        if drop_in == "Yes":
            drop_in = 1
        else:
            drop_in = 0
        # I honestly hate this but since we have 3 different selects which all can be multiple I think this is the only
        # way we can achieve the desired effect.
        for day in days_of_week:
            for tutor_name in tutor_names:
                # print(tutor_name)
                tutor = self.get_username_from_name(tutor_name)
                if tutor:
                    for time_slot in time_slots:
                        # Splits the time slot into a start time and end time
                        time_slot = time_slot.split('-')
                        start_ts = time_slot[0]
                        # Formats the meridiems to work with datetime
                        start_ts = start_ts.replace('a.m.', "AM")
                        start_ts = start_ts.replace('p.m.', "PM")
                        # Removes whitespace
                        start_ts = start_ts.strip()
                        # Formats the string into a datetime object
                        try:
                            start_ts = datetime.strptime(start_ts, '%H %p')
                        except:
                            start_ts = datetime.strptime(start_ts, '%H:%M %p')
                        end_ts = time_slot[1]
                        # Formats the meridiems to work with datetime
                        end_ts = end_ts.replace('a.m.', "AM")
                        end_ts = end_ts.replace('p.m.', "PM")
                        # Removes whitespace
                        end_ts = end_ts.strip()
                        # Formats the string into a datetime object
                        try:
                            end_ts = datetime.strptime(end_ts, '%H %p')
                        except:
                            end_ts = datetime.strptime(end_ts, '%H:%M %p')
                        appt_date = self.get_first_appointment_date(day, start_date)
                        while appt_date <= end_date:  # Loop through until our session date is after the end date of the term
                            # print('ot')
                            # Updates the datetime object with the correct date
                            # print(start_ts)
                            # print(tutor.firstName, tutor.lastName)
                            start_ts = start_ts.replace(year=appt_date.year, month=appt_date.month, day=appt_date.day)
                            end_ts = end_ts.replace(year=appt_date.year, month=appt_date.month, day=appt_date.day)
                            appointment = AppointmentsTable(tutor_id=tutor.id, scheduledStart=start_ts, scheduledEnd=end_ts,
                                                            inProgress=0, multilingual=multilingual, dropIn=drop_in, sub=0, noShow=0)
                            db_session.add(appointment)
                            db_session.commit()
                            appt_date += timedelta(weeks=1)  # Add a week for next session
        return None

    def get_first_appointment_date(self, week_day, start_date):
        first_date = start_date
        today = date.today()
        if today > first_date:
            first_date = today
        week_day = int(week_day)
        while True:
            # return the first day of the schedule after the semester starts
            if first_date.weekday() == week_day:  # Our DB Sunday = 0, Python datetime Monday = 0
                return first_date
            else:
                first_date += timedelta(days=1)  # if it hasn't matched, add a day and check again

    def get_tutor_appointments(self, tutors):
        appointment_list = []
        for tutor_id in tutors:
            tutor = self.get_user_by_id(tutor_id)
            if tutor:
                appointment_list.append(db_session.query(AppointmentsTable)
                                        .filter(AppointmentsTable.tutor_id == tutor.id)
                                        .all())

        return appointment_list

    def get_username_from_name(self, name):
        # Gets the tutor's first name, last name
        name = name.split(" ")
        firstname = name[0]
        lastname = name[1]
        # If a tutor has multiple last names, we use this loop to get them all
        if len(name) > 2:
            lastname = ""
            for i in range(1, len(name)):
                lastname += name[i] + " "
        # Gets the tutor's username
        name = self.get_user_by_name(firstname, lastname)
        return name

    def get_time_setting(self):
        return db_session.query(SettingsTable.value)\
            .filter(SettingsTable.id == 2)\
            .one_or_none()

    def delete_tutor_shifts(self, tutors, start_date, end_date):
        delete_list = []
        sub_list = []
        for tutor_id in tutors:
            tutor = self.get_user_by_id(tutor_id)
            if tutor:
                # Gets all of the appointments where no students are signed up for slots and 
                delete_list.append(db_session.query(AppointmentsTable)
                                   .filter(AppointmentsTable.tutor_id == tutor.id)
                                   .filter(AppointmentsTable.scheduledStart >= start_date)
                                   .filter(AppointmentsTable.scheduledEnd <= end_date)
                                   .filter(AppointmentsTable.student_id == None)
                                   .all())
                # Gets all the appointments where there is a student signed up for that we now potentially need
                # subtitutes for
                sub_list.append(db_session.query(AppointmentsTable)
                                .filter(AppointmentsTable.tutor_id == tutor.id)
                                .filter(AppointmentsTable.scheduledStart >= start_date)
                                .filter(AppointmentsTable.scheduledEnd <= end_date)
                                .filter(AppointmentsTable.sub == 0)
                                .filter(AppointmentsTable.student_id != None)
                                .all())
        try:
            for tutor_appts in delete_list:
                for appt in tutor_appts:
                    db_session.delete(appt)
            db_session.commit()
        except Exception:
            return False

        return sub_list

    def request_substitute(self, appt_id):
        # Requests a substitute for a specific appointment
        try:
            appointment = db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.id == appt_id)\
                .one_or_none()
            appointment.sub = 1
            db_session.commit()
            return True
        except Exception as e:
            return False

    def sub_all(self, appt_id_list):
        # Requests substitutes for all appointments in the list
        try:
            for appt_id in appt_id_list:
                appointment = db_session.query(AppointmentsTable)\
                    .filter(AppointmentsTable.id == appt_id)\
                    .one_or_none()
                appointment.sub = 1
            db_session.commit()
            return True
        except Exception as e:
            return False

