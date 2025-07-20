from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
# All models inherit from this base class
from db.setup_db import Base

class DetectionObject(Base):
    """
    Model for detection_objects table
    """
    __tablename__ = 'detection_objects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_uid = Column(String, ForeignKey('prediction_sessions.uid'), nullable=False)
    label = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    box = Column(String, nullable=False)









