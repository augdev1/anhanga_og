"""Seed database with initial data."""
import os
from database import get_db, UserORM, init_db


def seed():
    """Create default admin user if not exists."""
    init_db()
    db = get_db()
    
    try:
        # Check if admin exists
        admin = db.query(UserORM).filter(UserORM.username == "admin").first()
        if not admin:
            admin = UserORM(
                username="admin",
                name=os.getenv("TEST_LOGIN_NAME", "Admin"),
                password_hash=os.getenv("TEST_LOGIN_PASSWORD", "123456"),
                email=None,
                user_type=1  # Admin é tipo especial
            )
            db.add(admin)
            db.commit()
            print("[OK] Usuario admin criado (username: admin, password: 123456, tipo: 1)")
        else:
            # Garantir que admin tenha user_type=1
            if admin.user_type != 1:
                admin.user_type = 1
                db.commit()
                print("[OK] Usuario admin atualizado para tipo 1")
            else:
                print("[INFO] Usuario admin ja existe (tipo 1)")
            
    finally:
        db.close()


if __name__ == "__main__":
    seed()
