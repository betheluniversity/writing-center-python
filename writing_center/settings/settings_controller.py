from datetime import datetime

from writing_center.db_repository import db_session
from writing_center.db_repository.tables import SettingsTable, UserTable, UserRoleTable, RoleTable


class SettingsController:
    def __init__(self):
        pass

    def get_settings(self):
        return db_session.query(SettingsTable).all()

    def update_setting(self, setting_name, new_setting):
        setting = db_session.query(SettingsTable).filter(SettingsTable.name == setting_name).one()
        setting.value = new_setting
        db_session.commit()

    def cleanse(self):
        students = db_session.query(UserTable)\
            .filter(UserTable.id == UserRoleTable.user_id)\
            .filter(UserRoleTable.role_id == RoleTable.id)\
            .filter(RoleTable.name == "Student").all()
        for student in students:
            roles = db_session.query(UserRoleTable).filter(UserRoleTable.user_id == student.id).all()
            if len(roles) == 1:  # This means "Student" is their only role
                student.deletedAt = datetime.now()
        banned = db_session.query(UserTable).filter(UserTable.bannedDate != None).all()
        for ban in banned:
            ban.bannedDate = None
        db_session.commit()
