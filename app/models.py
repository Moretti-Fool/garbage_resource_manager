from datetime import datetime
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, DateTime, text
from sqlalchemy.orm import relationship
from .database import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(String, primary_key=True)
    filename = Column(String)
    expires_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

class UserVerification(Base):
    __tablename__ = "user_verifications"

    token = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    event = Column(String)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String)

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_superadmin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    last_login = Column(DateTime, nullable=True)

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    users = relationship("User", back_populates="role", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete="SET NULL"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    role = relationship("Role", back_populates="users")
