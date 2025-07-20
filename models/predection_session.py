from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
# All models inherit from this base class
from db.setup_db import Base



class PredictionSession(Base):
    """
    Model for prediction_sessions table
    """
    __tablename__ = 'prediction_sessions'
    
    uid = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    original_image = Column(String)
    predicted_image = Column(String)