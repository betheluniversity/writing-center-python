from sqlalchemy import Column, Integer, String, DateTime

from writing_center.db_repository import base


# TODO: below will be all the tables we use from the Writing Center DB below is an example from tutorlabs
class CourseCode_Table(base):
    __tablename__ = 'CourseCode'
    id = Column(Integer, primary_key=True)
    dept = Column(String)
    courseNum = Column(String)
    underived = Column(String)
    active = Column(Integer)
    courseName = Column(String)
