from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    
    # Config direta para garantir que funcione
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    PARENT_DIR = os.path.dirname(BASE_DIR)
    DB_PATH = os.path.join(PARENT_DIR, "instance", "app.db")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "dev-secret-key"
    app.config["DEBUG"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH.replace("\\", "/")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app
