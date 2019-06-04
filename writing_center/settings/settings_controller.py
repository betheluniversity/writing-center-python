from writing_center.db_repository import db_session
from writing_center.db_repository.tables import WCSystemSettingsTable

class SettingsController:
    def __init__(self):
        pass

    def get_settings(self):
        return db_session.query(WCSystemSettingsTable).filter(WCSystemSettingsTable.ID == 1).one()
