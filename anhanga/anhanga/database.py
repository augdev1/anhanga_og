"""Database module shared between Flask and FastAPI.

Uses SQLAlchemy core + ORM for async/sync compatibility.
"""

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Use same path as Flask config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "app.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"

# Engine for sync operations (FastAPI background, Flask)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()


class UserORM(Base):
    """User model for authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=True)
    name = Column(String(120), nullable=True)
    password_hash = Column(String(256), nullable=False)  # Store plain for now (dev only)
    user_type = Column(Integer, default=0)  # 0=normal, 1=especial/admin
    # Novos campos de perfil
    data_nasc = Column(String(10), nullable=True)  # DD/MM/AAAA
    telefone = Column(String(20), nullable=True)
    foto_url = Column(String(512), nullable=True)  # URL da foto ou base64
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReportORM(Base):
    """Reporte de queimada."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    user_id = Column(Integer, nullable=True)  # FK opcional
    username = Column(String(80), nullable=True)
    filename = Column(String(256), nullable=True)
    nivel = Column(String(20), default="alerta")  # alerta, suspeito, confirmado
    count = Column(Integer, default=1)
    is_confirmation = Column(Integer, default=0)  # 0=reporte original, 1=confirmacao
    created_at = Column(DateTime, default=datetime.utcnow)


class AuthTokenORM(Base):
    """Tokens ativos de autenticação."""
    __tablename__ = "auth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    username = Column(String(80), nullable=False)
    name = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def get_db_gen():
    """Generator version for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
