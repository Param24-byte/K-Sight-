from sqlalchemy import Column, Integer, String, DateTime
from src.services.db.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # Investigator, Analyst, Supervisor, Policymaker

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    action = Column(String)
    endpoint = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
