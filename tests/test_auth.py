# tests/test_auth.py
import pytest
from src.services import AuthService
from src.repositories import UserRepository
from src.database import DatabaseManager
from src.models import User
import os

# Fixture para base de datos en memoria (aislamiento)
@pytest.fixture
def db_manager():
    db = DatabaseManager(":memory:") # O una db de test temporal
    db.initialize_db()
    # Crear tabla de usuarios manualmente si initialize_db no lo tiene en el código fuente original aun
    with db.get_connection() as conn:
        conn.cursor().execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'admin'
            )
        """)
    return db

@pytest.fixture
def auth_service(db_manager):
    repo = UserRepository(db_manager)
    return AuthService(repo)

def test_register_user(auth_service):
    """Prueba que se puede registrar un usuario y se guarda el hash"""
    user = auth_service.register_user("testuser", "password123")
    assert user.id is not None
    assert user.username == "testuser"
    assert user.password_hash != "password123" # Debe estar hasheado

def test_register_duplicate_user(auth_service):
    """Prueba que no permite duplicados"""
    auth_service.register_user("user1", "pass")
    with pytest.raises(ValueError):
        auth_service.register_user("user1", "pass2")

def test_login_success(auth_service):
    """Prueba login exitoso"""
    auth_service.register_user("loginuser", "mypassword")
    logged_user = auth_service.login("loginuser", "mypassword")
    assert logged_user is not None
    assert logged_user.username == "loginuser"

def test_login_failure_wrong_password(auth_service):
    """Prueba fallo de contraseña"""
    auth_service.register_user("user2", "correctpass")
    logged_user = auth_service.login("user2", "wrongpass")
    assert logged_user is None

def test_login_failure_user_not_found(auth_service):
    """Prueba usuario inexistente"""
    logged_user = auth_service.login("ghost", "pass")
    assert logged_user is None