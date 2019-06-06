from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, UserRoleTable, RoleTable, WCEmailPreferencesTable

class UsersController:
    def __init__(self):
        pass

    def get_users(self):
        return db_session.query(UserTable, RoleTable)\
            .filter(UserTable.id == UserRoleTable.user_id)\
            .filter(UserRoleTable.role_id == RoleTable.id)\
            .all()

    def get_all_roles(self):
        return db_session.query(RoleTable)\
            .all()

    def get_user_by_username(self, username):
        return db_session.query(UserTable)\
            .filter(UserTable.username == username)\
            .one_or_none()

    def create_user(self, first_name, last_name, username, sub_email_pref, stu_email_pref):
        email_pref_id = self.create_email_preferences(sub_email_pref, stu_email_pref)
        new_user = UserTable(username=username, password=None, firstName=first_name, lastName=last_name,
                             email='{0}@bethel.edu'.format(username), email_pref_id=email_pref_id)
        db_session.add(new_user)
        db_session.commit()
        return new_user

    def create_email_preferences(self, sub_email_pref, stu_email_pref):
        new_email_prefs = WCEmailPreferencesTable(SubRequestEmail=sub_email_pref, StudentSignUpEmail=stu_email_pref)
        db_session.add(new_email_prefs)
        db_session.commit()

        return new_email_prefs.id

    def get_role_by_name(self, role_name):
        return db_session.query(RoleTable)\
            .filter(RoleTable.name == role_name)\
            .one()

    def set_user_roles(self, username, roles):
        user = self.get_user_by_username(username)
        for role in roles:
            role_entry = self.get_role_by_name(role)
            # Check if the user already has this role
            role_exists = db_session.query(UserRoleTable)\
                .filter(UserRoleTable.user_id == user.id)\
                .filter(UserRoleTable.role_id == role_entry.id)\
                .one_or_none()
            if role_exists:  # If they do, skip adding it again
                continue
            user_role = UserRoleTable(user_id=user.id, role_id=role_entry.id)
            db_session.add(user_role)
        db_session.commit()

    def get_user(self, user_id):
        return db_session.query(UserTable)\
            .filter(UserTable.id == user_id)\
            .one_or_none()

    def get_user_role_ids(self, user_id):
        user_roles = db_session.query(RoleTable)\
            .filter(RoleTable.id == UserRoleTable.role_id)\
            .filter(UserRoleTable.user_id == UserTable.id)\
            .filter(UserTable.id == user_id)\
            .all()
        user_role_ids = []
        for role in user_roles:
            user_role_ids.append(role.id)
        return user_role_ids

    def update_user_info(self, user_id, first_name, last_name, email):
        user = db_session.query(UserTable)\
            .filter(UserTable.id == user_id)\
            .one()
        user.firstName = first_name
        user.lastName = last_name
        user.email = email
        db_session.commit()

    def clear_current_roles(self, user_id):
        roles = db_session.query(UserRoleTable)\
            .filter(UserRoleTable.user_id == user_id)\
            .all()
        for role in roles:
            db_session.delete(role)
        db_session.commit()