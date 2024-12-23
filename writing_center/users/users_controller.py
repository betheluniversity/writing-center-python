from datetime import datetime

from flask import abort

from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable, UserRoleTable, RoleTable, EmailPreferencesTable, \
    AppointmentsTable
from writing_center.wsapi.wsapi_controller import WSAPIController


class UsersController:
    def __init__(self):
        self.wsapi = WSAPIController()

    def get_users(self):
        return db_session.query(UserTable, RoleTable)\
            .filter(UserTable.id == UserRoleTable.user_id)\
            .filter(UserRoleTable.role_id == RoleTable.id)\
            .filter(UserTable.deletedAt == None)\
            .all()

    def get_all_roles(self):
        return db_session.query(RoleTable).all()

    def get_user_by_username(self, username):
        return db_session.query(UserTable)\
            .filter(UserTable.username == username)\
            .one_or_none()

    def get_users_by_name(self, firstName, lastName):
        return db_session.query(UserTable)\
            .filter(UserTable.firstName.like('%{0}%'.format(firstName)))\
            .filter(UserTable.lastName.like('%{0}%'.format(lastName)))\
            .all()

    def create_user(self, first_name, last_name, username, sub_email_pref, stu_email_pref):
        new_user = UserTable(username=username, firstName=first_name, lastName=last_name,
                             email='{0}@bethel.edu'.format(username), bannedDate=None, deletedAt=None)
        db_session.add(new_user)
        db_session.commit()
        self.create_email_preferences(new_user.id, sub_email_pref, stu_email_pref)
        return new_user

    def create_email_preferences(self, user_id, sub_email_pref, stu_email_pref):
        new_email_prefs = EmailPreferencesTable(user_id=user_id, subRequestEmail=sub_email_pref, studentSignUpEmail=stu_email_pref)
        db_session.add(new_email_prefs)
        db_session.commit()

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

    def get_user_by_id(self, user_id):
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

    def get_future_user_appointments(self, user_id):
        return db_session.query(AppointmentsTable)\
            .filter(AppointmentsTable.student_id == user_id)\
            .filter(AppointmentsTable.scheduledStart > datetime.now())\
            .all()

    def cancel_appointment(self, appt_id):
        try:
            appt = db_session.query(AppointmentsTable)\
                .filter(AppointmentsTable.id == appt_id)\
                .one_or_none()
            appt.student_id = None
            appt.profName = None
            appt.profEmail = None
            appt.assignment = None
            appt.courseCode = None
            appt.courseSection = None
            db_session.commit()
            return True
        except Exception as e:
            return False

    def get_user_roles(self, user_id):
        user_roles = db_session.query(RoleTable)\
            .filter(RoleTable.id == UserRoleTable.role_id)\
            .filter(UserRoleTable.user_id == UserTable.id)\
            .filter(UserTable.id == user_id)\
            .all()
        return user_roles

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

    def get_banned_users(self):
        return db_session.query(UserTable)\
            .filter(UserTable.bannedDate != None)\
            .all()

    def remove_user_ban(self, user_id):
        banned_user = db_session.query(UserTable)\
            .filter(UserTable.id == user_id)\
            .filter(UserTable.bannedDate != None)\
            .one_or_none()
        if banned_user:
            banned_user.bannedDate = None
            db_session.commit()

    def remove_all_bans(self):
        banned_users = db_session.query(UserTable).filter(UserTable.bannedDate != None).all()
        if banned_users:
            for user in banned_users:
                user.bannedDate = None
            db_session.commit()

    def ban_user(self, username):
        now = datetime.now()
        user = self.get_user_by_username(username)
        user.bannedDate = now
        db_session.commit()

    def deactivate_user(self, user_id):
        user = self.get_user_by_id(user_id)
        user.deletedAt = datetime.now()
        db_session.commit()

    def activate_existing_user(self, user_id):
        try:
            user = self.get_user_by_id(user_id)
            user.deletedAt = None
            db_session.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def create_user_at_sign_in(self, username):
        wsapi_names = self.wsapi.get_names_from_username(username)
        if not wsapi_names:
            return abort(403)
        names = wsapi_names['0']
        first_name = names['firstName']
        if names['prefFirstName']:
            first_name = names['prefFirstName']
        last_name = names['lastName']

        student = None
        roles = self.wsapi.get_roles_for_username(username)
        for role in roles:
            if 'STUDENT-CAS' == roles[role]['userRole']:
                student = self.create_user(first_name, last_name, username, 0, 0)
                self.set_user_roles(username, ['Student'])
        
        return student
