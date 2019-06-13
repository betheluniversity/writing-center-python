from datetime import datetime

from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, WCAppointmentDataTable


class AppointmentsController:
    def __init__(self):
        pass

    def get_user_by_username(self, username):
        return db_session.query(UserTable)\
            .filter(UserTable.username == username)\
            .one_or_none()

    def get_filled_appointments(self):
        return db_session.query(WCAppointmentDataTable)\
            .filter(WCAppointmentDataTable.StudUsername != "")\
            .filter(WCAppointmentDataTable.StudUsername != None)\
            .all()

    def get_yearly_appointments(self, selected_year):
        test = db_session.query(WCAppointmentDataTable)\
            .filter(WCAppointmentDataTable.StudUsername != "")\
            .filter(WCAppointmentDataTable.StudUsername != None)\
            .all()
        tt = []
        for t in test:
            if int(t.StartTime.strftime('%Y')) == selected_year:
                tt.append(t)
        return tt

    def get_years(self):
        years = [2014]
        year = 2015
        current_year = datetime.now()
        current_year = int(current_year.strftime('%Y'))
        while year <= current_year:
            years.append(year)
            year += 1
        return years

