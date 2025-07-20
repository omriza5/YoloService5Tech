from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from datetime import datetime
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
    timestamp = Column(DateTime, default=datetime.utcnow)









