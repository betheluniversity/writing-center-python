from sqlalchemy import Column, Integer, DateTime, Time, VARCHAR, ForeignKey

from writing_center.db_repository import base


class AppointmentsTable(base):
    __tablename__ = 'Appointments'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('User.id'))
    tutor_id = Column(Integer, ForeignKey('User.id'))
    scheduledStart = Column(DateTime)
    scheduledEnd = Column(DateTime)
    actualStart = Column(DateTime)
    actualEnd = Column(DateTime)
    profName = Column(VARCHAR(255))
    profEmail = Column(VARCHAR(255))
    dropIn = Column(Integer)
    sub = Column(Integer)
    assignment = Column(VARCHAR(255))
    notes = Column(VARCHAR(255))
    suggestions = Column(VARCHAR(255))
    multilingual = Column(Integer)
    courseCode = Column(VARCHAR(10))
    courseSection = Column(Integer)
    noShow = Column(Integer)
    inProgress = Column(Integer)
    online = Column(Integer)
    pseo = Column(Integer)


class EmailPreferencesTable(base):
    __tablename__ = 'EmailPreferences'
    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    subRequestEmail = Column(Integer)
    studentSignUpEmail = Column(Integer)


class RoleTable(base):
    __tablename__ = 'Role'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255))


class ScheduleTable(base):
    __tablename__ = 'Schedule'
    id = Column(Integer, primary_key=True)
    startTime = Column(Time)
    endTime = Column(Time)
    active = Column(Integer)


class SettingsTable(base):
    __tablename__ = 'Settings'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255))
    value = Column(VARCHAR(255))


class UserTable(base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(255))
    email = Column(VARCHAR(255))
    firstName = Column(VARCHAR(255))
    lastName = Column(VARCHAR(255))
    bannedDate = Column(DateTime)
    deletedAt = Column(DateTime)


class UserRoleTable(base):
    __tablename__ = 'user_role'
    user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('Role.id'), primary_key=True)
