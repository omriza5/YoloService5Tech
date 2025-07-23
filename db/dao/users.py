from models.user import User

def get_user_by_username_dao(db, username):
    """
    Get user by username
    """
    return db.query(User).filter(User.username == username).first()
    
def create_user_dao(db, user):
    """
    Create a new user in the database
    """
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


