from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from writing_center import app

constr = app.config['CON_STRING']

bw = True
if bw:
    constr %= app.config['DB_KEY_BW']
else:
    constr %= app.config['DB_KEY']


engine_bw = create_engine(constr, convert_unicode=True)
db_session_bw = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine_bw))
conn_bw = engine_bw.raw_connection()
call_cursor_bw = conn_bw.cursor()
result_cursor_bw = conn_bw.cursor()

Base = declarative_base()
Base.query = db_session_bw.query_property()

def init_db_bw():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()

    Base.metadata.create_all(bind=engine_bw)