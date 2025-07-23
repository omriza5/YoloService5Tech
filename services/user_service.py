import bcrypt
from fastapi import HTTPException
from models.user import User
from db.dao.users import get_user_by_username_dao, create_user_dao

def create_new_user(username, password, db):
    if not username or not password or username.strip() == "" or password.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    
    username = username.lower().strip()
    
    existing_user = get_user_by_username_dao(db, username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    
    user = User(username=username, password=hashed_pw)
    create_user_dao(db, user)
    
    return {"detail": "User created successfully"}
        
        