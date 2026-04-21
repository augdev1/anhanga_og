"""Flask-SQLAlchemy models - compatível com database.py."""
from app import db


class User(db.Model):
    """User model - mapeia para mesma tabela do UserORM."""
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<User {self.username}>"
