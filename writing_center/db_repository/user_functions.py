from datetime import datetime, timedelta
from sqlalchemy import orm
from flask import session as flask_session
from writing_center.db_repository import db_session
from writing_center.db_repository.tables import UserTable


class UserFunctions:
    def get_user(self, username):
        return (db_session.query(UserTable)
                .filter(UserTable.username == username)
                .all())
