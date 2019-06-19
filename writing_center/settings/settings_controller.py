from writing_center.db_repository import db_session
from writing_center.db_repository.tables import WCSystemSettingsTable

class SettingsController:
    def __init__(self):
        pass

    def get_settings(self):
        return db_session.query(WCSystemSettingsTable).filter(WCSystemSettingsTable.ID == 1).one()

    def update_setting(self, setting_name, new_setting):
        settings = self.get_settings()
        if setting_name == 'apptLimit':
            settings.apptLimit = new_setting
        elif setting_name == 'timeLimit':
            settings.timeLimit = new_setting
        elif setting_name == 'banLimit':
            settings.banLimit = new_setting
        else:
            settings.qualtricsLink = new_setting
        db_session.commit()
