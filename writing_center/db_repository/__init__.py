from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine

# Local
from writing_center import app

# pool_pre_ping allows us to avoid timeout errors
db = create_engine(app.config['DATABASE_KEY'], convert_unicode=True, pool_pre_ping=True)
base = declarative_base()
session_maker = sessionmaker(bind=db, autoflush=False)
db_session = session_maker()
