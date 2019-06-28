from writing_center.db_repository import db_session
from writing_center.db_repository.tables import SettingsTable


class SettingsController:
    def __init__(self):
        pass

    def get_settings(self):
        return db_session.query(SettingsTable).all()

    def update_setting(self, setting_name, new_setting):
        setting = db_session.query(SettingsTable).filter(SettingsTable.name == setting_name).one()
        setting.value = new_setting
        db_session.commit()
