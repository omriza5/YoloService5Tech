import os
from db.setup_db import SessionLocal, Base, engine
# Dont remove models imports, it is necessary for the models to be registered
import models.detection_object
import models.predection_session
import models.user
# END of models imports

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Drop all tables to clean the database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine)  