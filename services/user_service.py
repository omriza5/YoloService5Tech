import bcrypt
from fastapi import HTTPException
from models.user import User

def create_new_user(username, password, db):
    if not username or not password or username.strip() == "" or password.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    
    username = username.lower().strip()
    
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    
    user = User(username=username, password=hashed_pw)
    db.add(user)
    db.commit()
    return {"detail": "User created successfully"}
        
        