import pytest
from src.services import AuthService
from src.repositories import UserRepository
from src.database import DatabaseManager

# Fixture para base de datos en memoria (aislada por cada test si se necesita)
@pytest.fixture
def auth_service():
    db = DatabaseManager(":memory:")
    db.initialize_db()
    repo = UserRepository(db)
    return AuthService(repo)

def test_register_and_login_flow(auth_service):
    # 1. Registro
    user = auth_service.register_user("admin_test", "securePass123")
    assert user.id is not None
    assert user.password_hash != "securePass123"
    
    # 2. Login Exitoso
    logged_user = auth_service.login("admin_test", "securePass123")
    assert logged_user is not None
    assert logged_user.username == "admin_test"

def test_login_wrong_credentials(auth_service):
    auth_service.register_user("user", "pass")
    
    # Password incorrecto
    assert auth_service.login("user", "wrong") is None
    # Usuario incorrecto
    assert auth_service.login("nobody", "pass") is None

def test_register_duplicate_user(auth_service):
    auth_service.register_user("unico", "pass")
    with pytest.raises(ValueError, match="El usuario ya existe"):
        auth_service.register_user("unico", "otra_pass")

def test_create_admin_idempotency(auth_service):
    """Prueba que create_admin_if_not_exists no duplique ni falle si ya existe."""
    # Primera vez: crea
    auth_service.create_admin_if_not_exists()
    assert auth_service.login("admin", "admin123") is not None
    
    # Segunda vez: no hace nada (no debe fallar)
    auth_service.create_admin_if_not_exists()
    # Verificar que sigue existiendo y funcionando
    assert auth_service.login("admin", "admin123") is not None