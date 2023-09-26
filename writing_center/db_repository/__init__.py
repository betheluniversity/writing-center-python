import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

# Local
from writing_center import app


if os.environ.get('MYSQL_DATABASE_SERVER'):
    DATABASE_USER = os.environ.get('MYSQL_DATABASE_USER')
    DATABASE_PASSWORD = os.environ.get('MYSQL_DATABASE_PASSWORD')
    DATABASE_SERVER = os.environ.get('MYSQL_DATABASE_SERVER')
    DATABASE_PORT = os.environ.get('MYSQL_DATABASE_PORT')
    DATABASE_NAME = os.environ.get('MYSQL_DATABASE_NAME')
elif app.config.get('ENVIRON') == 'prod':
    DATABASE_USER = app.config.get('DATABASE_USER')
    DATABASE_PASSWORD = app.config.get('DATABASE_PASSWORD')
    DATABASE_SERVER = app.config.get('DATABASE_SERVER_PROD')
    DATABASE_PORT = app.config.get('DATABASE_PORT')
    DATABASE_NAME = app.config.get('DATABASE_NAME_PROD')
else:
    DATABASE_USER = app.config.get('DATABASE_USER')
    DATABASE_PASSWORD = app.config.get('DATABASE_PASSWORD')
    DATABASE_SERVER = app.config.get('DATABASE_SERVER_DEV')
    DATABASE_PORT = app.config.get('DATABASE_PORT')
    DATABASE_NAME = app.config.get('DATABASE_NAME_DEV')

    if os.environ.get('DEV_SSH_TUNNEL_SQL_SERVER', ''):
        DATABASE_SERVER = '0.0.0.0'

DATABASE_KEY = 'mysql://{0}:{1}@{2}:{3}/{4}'.format(DATABASE_USER, DATABASE_PASSWORD, DATABASE_SERVER, DATABASE_PORT, DATABASE_NAME)

# pool_pre_ping allows us to avoid timeout errors
db = create_engine(DATABASE_KEY, convert_unicode=True, pool_pre_ping=True)
base = declarative_base()
session_maker = sessionmaker(bind=db, autoflush=False)
db_session = scoped_session(session_maker)
