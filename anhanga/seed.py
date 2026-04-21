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
                name=os.getenv("TEST_LOGIN_NAME", "Administrador"),
                password_hash=os.getenv("TEST_LOGIN_PASSWORD", "admin12345"),  # min 8 chars
                email="admin@anhanga.local",
                data_nasc="1990-01-01",  # maior de 12 anos
                telefone="0000000000",
                foto_url="",  # foto vazia inicialmente
                user_type=1  # 1 = ativo (admin já nasce aprovado)
            )
            db.add(admin)
            db.commit()
            print("[OK] Usuario admin criado (username: admin, password: admin12345, tipo: 1)")
        else:
            # Garantir que admin tenha user_type=1 (ativo) e dados obrigatorios
            updated = False
            if admin.user_type != 1:
                admin.user_type = 1
                updated = True
            if not admin.email:
                admin.email = "admin@anhanga.local"
                updated = True
            if not admin.data_nasc:
                admin.data_nasc = "1990-01-01"
                updated = True
            if not admin.telefone:
                admin.telefone = "0000000000"
                updated = True
            if updated:
                db.commit()
                print("[OK] Usuario admin atualizado (tipo 1 + dados obrigatorios)")
            else:
                print("[INFO] Usuario admin ja existe (tipo 1, ativo)")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
