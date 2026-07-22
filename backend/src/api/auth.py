from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from src.services.db.database import get_db
from src.services.db.models import User
from pydantic import BaseModel
import os

SECRET_KEY = os.getenv("SECRET_KEY", "HACKATHON_SUPER_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

class Token(BaseModel):
    access_token: str
    token_type: str
    
class RoleSwitchRequest(BaseModel):
    role: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(allowed_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted for this role")
        return current_user
    return role_checker

@router.post("/token", response_model=Token)
def login_for_access_token(req: RoleSwitchRequest, db: Session = Depends(get_db)):
    """Mock login endpoint that issues a token for a specific role (for Datathon demo)"""
    allowed = ["Investigator", "Analyst", "Supervisor", "Policymaker"]
    if req.role not in allowed:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    user = db.query(User).filter(User.role == req.role).first()
    if not user:
        # Auto-provision mock users for the datathon demo
        user = User(username=f"demo_{req.role.lower()}", hashed_password="fakehash", role=req.role)
        db.add(user)
        db.commit()
        db.refresh(user)
        
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
