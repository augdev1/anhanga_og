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
    user_type = Column(Integer, default=0)  # 0=pendente, 1=ativo, 2=especial (admin username="admin")
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
    fonte = Column(String(50), nullable=True)  # fonte do reporte: comunidade, tupa, etc.
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


class ActivityLogORM(Base):
    """Log de atividades dos usuários no sistema."""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # login, report, map_view, etc
    details = Column(Text, nullable=True)  # JSON ou descrição da ação
    ip_address = Column(String(45), nullable=True)  # IPv4 ou IPv6
    user_agent = Column(String(256), nullable=True)  # Browser info
    created_at = Column(DateTime, default=datetime.utcnow)


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


def log_activity(username: str, action: str, details: str = None, ip_address: str = None, user_agent: str = None):
    """Registra uma atividade do usuário no sistema."""
    db = SessionLocal()
    try:
        log = ActivityLogORM(
            username=username,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def get_online_users(db: Session, minutes: int = 30):
    """Retorna usuários com token ativo nos últimos X minutos."""
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)

    # Buscar tokens ativos criados nos últimos X minutos
    tokens = db.query(AuthTokenORM).filter(AuthTokenORM.created_at >= cutoff).all()

    # Agrupar por username (evitar duplicados) - pegar o token mais recente
    seen = {}
    for token in tokens:
        if token.username not in seen or token.created_at > seen[token.username]:
            seen[token.username] = token.created_at

    # Montar lista final com dados dos usuários
    online_users = []
    for username, last_activity in seen.items():
        user = db.query(UserORM).filter(UserORM.username == username).first()
        if user:
            online_users.append({
                "username": user.username,
                "name": user.name,
                "foto_url": user.foto_url,
                "last_activity": last_activity.isoformat()
            })

    return online_users


def get_recent_activities(db: Session, limit: int = 50):
    """Retorna as atividades mais recentes do sistema."""
    logs = db.query(ActivityLogORM).order_by(ActivityLogORM.created_at.desc()).limit(limit).all()
    return [{
        "id": log.id,
        "username": log.username,
        "action": log.action,
        "details": log.details,
        "created_at": log.created_at.isoformat()
    } for log in logs]
