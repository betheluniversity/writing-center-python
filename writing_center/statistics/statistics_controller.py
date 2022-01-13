from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, AppointmentsTable, ScheduleTable


class StatisticsController:
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

    def get_appt_hours(self, start, end, username):
        user = self.get_user_by_username(username)
        appointments = db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.tutor_id == user.id)\
            .filter(AppointmentsTable.actualStart >= start)\
            .filter(AppointmentsTable.actualEnd <= end)\
            .all()

        time = 0

        for appointment in appointments:
            start_time = str(appointment.scheduledStart).split(' ')[1].split(':')
            start_min = int(start_time[1])
            start_hour = int(start_time[0])
            if 0 < start_min < 15:
                start_min = 15
            elif 15 < start_min < 30:
                start_min = 30
            elif 30 < start_min < 45:
                start_min = 45
            elif 45 < start_min < 60:
                start_min = 0
                if start_hour < 24:
                    start_hour += 1
            end_time = str(appointment.scheduledEnd).split(' ')[1].split(':')
            end_min = int(end_time[1])
            end_hour = int(end_time[0])
            if 0 < end_min < 15:
                end_min = 15
            elif 15 < end_min < 30:
                end_min = 30
            elif 30 < end_min < 45:
                end_min = 45
            elif 45 < end_min < 60:
                end_min = 0
                if end_hour < 24:
                    end_hour += 1
            time += end_hour - start_hour + (end_min - start_min) / 60

        return appointments, time

    def get_appointments(self, start, end, value):
        if value == 'all':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.scheduledStart >= start)\
                .filter(AppointmentsTable.scheduledEnd <= end)\
                .filter(AppointmentsTable.scheduledStart != AppointmentsTable.scheduledEnd)\
                .filter(AppointmentsTable.student_id)\
                .filter(AppointmentsTable.tutor_id)\
                .all()
        elif value == 'non':
            return db_session.query(AppointmentsTable) \
                .filter(AppointmentsTable.multilingual == 0)\
                .filter(AppointmentsTable.scheduledStart >= start)\
                .filter(AppointmentsTable.scheduledEnd <= end) \
                .filter(AppointmentsTable.scheduledStart != AppointmentsTable.scheduledEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 0) \
                .all()
        elif value == 'multilingual':
            return db_session.query(AppointmentsTable) \
                .filter(AppointmentsTable.multilingual == 1) \
                .filter(AppointmentsTable.scheduledStart >= start) \
                .filter(AppointmentsTable.scheduledEnd <= end) \
                .filter(AppointmentsTable.scheduledStart != AppointmentsTable.scheduledEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 0) \
                .all()
        elif value == 'non-virtual':
            return db_session.query(AppointmentsTable) \
                .filter(AppointmentsTable.scheduledStart >= start) \
                .filter(AppointmentsTable.scheduledEnd <= end) \
                .filter(AppointmentsTable.scheduledStart != AppointmentsTable.scheduledEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 0) \
                .all()
        elif value == 'virtual':
            return db_session.query(AppointmentsTable) \
                .filter(AppointmentsTable.multilingual == 0) \
                .filter(AppointmentsTable.scheduledStart >= start) \
                .filter(AppointmentsTable.scheduledEnd <= end) \
                .filter(AppointmentsTable.scheduledStart != AppointmentsTable.scheduledEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 1) \
                .all()
        elif value == 'virtual-multilingual':
            return db_session.query(AppointmentsTable) \
                .filter(AppointmentsTable.multilingual == 1) \
                .filter(AppointmentsTable.scheduledStart >= start) \
                .filter(AppointmentsTable.scheduledEnd <= end) \
                .filter(AppointmentsTable.scheduledStart != AppointmentsTable.scheduledEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 1) \
                .all()
        else:
            return False

    def get_walk_in_appointments(self, start, end, value):
        if value == 'all':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.dropIn == 1)\
                .filter(AppointmentsTable.actualStart >= start)\
                .filter(AppointmentsTable.actualEnd <= end) \
                .filter(AppointmentsTable.actualStart != AppointmentsTable.actualEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .all()
        elif value == 'non':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.dropIn == 1)\
                .filter(AppointmentsTable.multilingual == 0)\
                .filter(AppointmentsTable.actualStart >= start)\
                .filter(AppointmentsTable.actualEnd <= end) \
                .filter(AppointmentsTable.actualStart != AppointmentsTable.actualEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 0) \
                .all()
        elif value == 'multilingual':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.dropIn == 1)\
                .filter(AppointmentsTable.multilingual == 1)\
                .filter(AppointmentsTable.actualStart >= start)\
                .filter(AppointmentsTable.actualEnd <= end) \
                .filter(AppointmentsTable.actualStart != AppointmentsTable.actualEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 0) \
                .all()
        elif value == 'non-virtual':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.dropIn == 1)\
                .filter(AppointmentsTable.actualStart >= start)\
                .filter(AppointmentsTable.actualEnd <= end) \
                .filter(AppointmentsTable.actualStart != AppointmentsTable.actualEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 0) \
                .all()
        elif value == 'virtual':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.dropIn == 1)\
                .filter(AppointmentsTable.multilingual == 0)\
                .filter(AppointmentsTable.actualStart >= start)\
                .filter(AppointmentsTable.actualEnd <= end) \
                .filter(AppointmentsTable.actualStart != AppointmentsTable.actualEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 1) \
                .all()
        elif value == 'virtual-multilingual':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.dropIn == 1)\
                .filter(AppointmentsTable.multilingual == 1)\
                .filter(AppointmentsTable.actualStart >= start)\
                .filter(AppointmentsTable.actualEnd <= end) \
                .filter(AppointmentsTable.actualStart != AppointmentsTable.actualEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 1) \
                .all()
        else:
            return False

    def get_no_show_appointments(self, start, end, value):
        if value == 'all':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.noShow == 1)\
                .filter(AppointmentsTable.scheduledStart >= start)\
                .filter(AppointmentsTable.scheduledEnd <= end) \
                .filter(AppointmentsTable.scheduledStart != AppointmentsTable.scheduledEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .all()
        elif value == 'non':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.noShow == 1)\
                .filter(AppointmentsTable.multilingual == 0)\
                .filter(AppointmentsTable.scheduledStart >= start)\
                .filter(AppointmentsTable.scheduledEnd <= end) \
                .filter(AppointmentsTable.scheduledStart != AppointmentsTable.scheduledEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 0) \
                .all()
        elif value == 'multilingual':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.noShow == 1)\
                .filter(AppointmentsTable.multilingual == 1)\
                .filter(AppointmentsTable.scheduledStart >= start)\
                .filter(AppointmentsTable.scheduledEnd <= end) \
                .filter(AppointmentsTable.scheduledStart != AppointmentsTable.scheduledEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 0) \
                .all()
        elif value == 'non-virtual':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.noShow == 1)\
                .filter(AppointmentsTable.scheduledStart >= start)\
                .filter(AppointmentsTable.scheduledEnd <= end) \
                .filter(AppointmentsTable.scheduledStart != AppointmentsTable.scheduledEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 0) \
                .all()
        elif value == 'virtual':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.noShow == 1)\
                .filter(AppointmentsTable.multilingual == 0)\
                .filter(AppointmentsTable.scheduledStart >= start)\
                .filter(AppointmentsTable.scheduledEnd <= end) \
                .filter(AppointmentsTable.scheduledStart != AppointmentsTable.scheduledEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 1) \
                .all()
        elif value == 'virtual-multilingual':
            return db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.noShow == 1)\
                .filter(AppointmentsTable.multilingual == 1)\
                .filter(AppointmentsTable.scheduledStart >= start)\
                .filter(AppointmentsTable.scheduledEnd <= end) \
                .filter(AppointmentsTable.scheduledStart != AppointmentsTable.scheduledEnd) \
                .filter(AppointmentsTable.student_id) \
                .filter(AppointmentsTable.tutor_id) \
                .filter(AppointmentsTable.online == 1) \
                .all()
        else:
            return False

    def datetimeformat(self, value, custom_format=None):
        if value:
            if custom_format:
                return value.strftime(custom_format)

            if value.strftime('%l:%M:%p') == '12:00AM':  # Check for midnight
                return 'midnight'

            if value.strftime('%l:%M:%p') == '12:00PM':  # Check for noon
                return 'noon'

            if value.strftime('%M') == '00':
                time = value.strftime('%l')
            else:
                time = value.strftime('%l:%M')

            if value.strftime('%p') == 'PM':
                time = '{0} {1}'.format(time, 'p.m.')
            else:
                time = '{0} {1}'.format(time, 'a.m.')

            return time

        else:
            return '???'
