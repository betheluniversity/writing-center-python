from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, RoleTable

class ProfileController:
    def __init__(self):
        pass

    def get_user_by_username(self, username):
        return db_session.query(UserTable)\
            .filter(UserTable.username == username)\
            .one_or_none()

    def edit_user(self, first_name, last_name, username):
        user_to_edit = self.get_user_by_username(username)
        user_to_edit.firstName = first_name
        user_to_edit.lastName = last_name
        db_session.commit()

    def get_all_roles(self):
        return db_session.query(RoleTable).all()

    def get_role(self, role_id):
        return db_session.query(RoleTable).filter(RoleTable.id == role_id).one()
