from sqlalchemy import Column, Integer, String, DateTime

from writing_center.db_repository import base


class RoleTable(base):
    __tablename__ = 'Role'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    role = Column(String(20), unique=True)


class UserTable(base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    email_pref_id = Column(Integer, unique=True)
    password = Column(String(64))
    username = Column(String(255))
    email = Column(String(255))
    firstName = Column(String(255))
    lastName = Column(String(255))


class UserRoleTable(base):
    __tablename__ = 'user_role'
    user_id = Column(Integer, primary_key=True)
    role_id = Column(Integer, primary_key=True)


class WCAppointmentDataTable(base):
    __tablename__ = 'WCAppointmentData'
    ID = Column(Integer, primary_key=True)
    StudUsername = Column(String(255))
    TutorUsername = Column(String(255))
    Program = Column(String(255))
    StartTime = Column(DateTime)
    EndTime = Column(DateTime)
    ActualStartTime = Column(DateTime)
    CompletedTime = Column(DateTime)
    CheckIn = Column(Integer)
    StudentSignIn = Column(DateTime)
    StudentSignOut = Column(DateTime)
    ProfEmail = Column(String(255))
    RequestSub = Column(String(255))
    Assignment = Column(String(255))
    Notes = Column(String(255))
    Suggestions = Column(String(255))
    multilingual = Column(Integer)
    CourseCode = Column(String(255))
    ProfUsername = Column(String(255))
    CourseSection = Column(Integer)
    DropInAppt = Column(Integer)


class WCDropInAppointmentsTable(base):
    __tablename__ = 'WCDropInAppointments'
    ID = Column(Integer, primary_key=True)
    StartTime = Column(DateTime)
    EndTime = Column(DateTime)


class WCEmailPreferencesTable(base):
    __tablename__ = 'WCEmailPreferences'
    id = Column(Integer, primary_key=True)
    SubRequestEmail = Column(Integer)
    StudentSignUpEmail = Column(Integer)


class WCScheduleTable(base):
    __tablename__ = 'WCSchedule'
    ID = Column(Integer, primary_key=True)
    timeStart = Column(DateTime)
    timeEnd = Column(DateTime)
    isActive = Column(String(255))


class WCStudentBansTable(base):
    __tablename__ = 'WCStudentBans'
    user_id = Column(Integer, unique=True)
    ID = Column(Integer, primary_key=True)
    bannedDate = Column(DateTime)
    Username = Column(String(255))


class WCSystemSettingsTable(base):
    __tablename__ = 'WCSystemSettings'
    ID = Column(Integer, primary_key=True)
    apptLimit = Column(Integer)
    timeLimit = Column(Integer)
    banLimit = Column(Integer)
    qualtricsLink = Column(String(255))
