from fastapi import Request
from fastapi.responses import JSONResponse
from app import app
import base64
import bcrypt
from db.setup_db import SessionLocal
from models.user import User

@app.middleware("http")
async def basic_auth_middleware(request: Request, call_next):
    # Allow /health without auth
    if request.url.path == "/health" or request.url.path == "/users":
        return await call_next(request)
    
    # Extract Basic Auth from headers
    username, password = get_credentials_from_headers(request)
    user_id= verify_credentials(username,password)
    
    if request.method == "POST" and request.url.path == "/predict":
        request.state.user_id = user_id
        return await call_next(request)
    
    if not user_id:
        # If credentials are not provided or invalid, raise HTTPException
         return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized"},
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return await call_next(request)



def get_credentials_from_headers(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Basic "):
        encoded_credentials = auth_header.split(" ", 1)[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)
        return username, password
    return None, None


def verify_credentials(username: str, user_password: str):
    if not username or not user_password:
        return None
    username = username.lower().strip()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if bcrypt.checkpw(user_password.encode("utf-8"), user.password.encode("utf-8")):
            return user.id
        return None
    finally:
        db.close()