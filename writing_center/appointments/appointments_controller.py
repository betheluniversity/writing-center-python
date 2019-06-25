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
        yearly_appts = db_session.query(WCAppointmentDataTable)\
            .filter(WCAppointmentDataTable.StudUsername != "")\
            .filter(WCAppointmentDataTable.StudUsername != None)\
            .all()
        appts_list = []
        for appts in yearly_appts:
            if int(appts.StartTime.strftime('%Y')) == selected_year:
                appts_list.append(appts)
        return appts_list

    def get_all_user_appointments(self, username):
        return db_session.query(WCAppointmentDataTable)\
            .filter(WCAppointmentDataTable.StudUsername == username)\
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
        return db_session.query(WCAppointmentDataTable)\
            .filter(WCAppointmentDataTable.StartTime > datetime.now())\
            .all()

    def create_appointment(self):
        pass
        # appointment = WCAppointmentDataTable(StudUsername=, TutorUsername=, StartTime=, EndTime=)

        # ID = Column(Integer, primary_key=True)
        # StudUsername = Column(String(255))
        # TutorUsername = Column(String(255))
        # Program = Column(String(255))
        # StartTime = Column(DateTime)
        # EndTime = Column(DateTime)
        # ActualStartTime = Column(DateTime)
        # CompletedTime = Column(DateTime)
        # CheckIn = Column(Integer)
        # StudentSignIn = Column(DateTime)
        # StudentSignOut = Column(DateTime)
        # ProfEmail = Column(String(255))
        # RequestSub = Column(String(255))
        # Assignment = Column(String(255))
        # Notes = Column(String(255))
        # Suggestions = Column(String(255))
        # multilingual = Column(Integer)
        # CourseCode = Column(String(255))
        # ProfUsername = Column(String(255))
        # CourseSection = Column(Integer)
        # DropInAppt = Column(Integer)

