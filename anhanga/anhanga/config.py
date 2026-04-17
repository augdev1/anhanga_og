import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    DEBUG = True
    # SQLite path - usa mesma pasta instance/
    DB_PATH = os.path.join(BASE_DIR, "instance", "app.db")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DB_PATH.replace("\\", "/")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
