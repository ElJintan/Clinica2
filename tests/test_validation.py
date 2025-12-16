import pytest
from unittest.mock import Mock
from datetime import date
from src.services import ClinicService
from src.models import Client, Pet

# Fixture para inicializar el servicio con Mocks
@pytest.fixture
def service():
    client_repo = Mock()
    pet_repo = Mock()
    appt_repo = Mock()
    mr_repo = Mock()
    bill_repo = Mock()
    review_repo = Mock()
    
    # Configurar retorno exitoso simulado para create
    client_repo.create.side_effect = lambda x: x
    pet_repo.create.side_effect = lambda x: x
    
    return ClinicService(client_repo, pet_repo, appt_repo, mr_repo, bill_repo, review_repo)

# --- Test de Cliente ---

def test_add_client_success(service):
    """Prueba que un cliente válido se crea correctamente."""
    client = service.add_client("Ana", "ana@test.com", "123456789")
    assert client.name == "Ana"
    service.client_repo.create.assert_called_once()

def test_add_client_invalid_email(service):
    """Debe fallar si el email no tiene formato correcto."""
    with pytest.raises(ValueError, match="Email inválido"):
        service.add_client("Ana", "ana-sin-arroba.com", "123456789")
    service.client_repo.create.assert_not_called()

def test_add_client_invalid_phone(service):
    """Debe fallar si el teléfono tiene letras."""
    with pytest.raises(ValueError, match="Teléfono inválido"):
        service.add_client("Ana", "ana@test.com", "abc-123")
    service.client_repo.create.assert_not_called()

def test_add_client_empty_name(service):
    """Debe fallar si el nombre está vacío."""
    with pytest.raises(ValueError, match="El nombre del cliente no puede estar vacío"):
        service.add_client("", "ana@test.com", "123456789")

# --- Test de Mascota ---

def test_add_pet_negative_age(service):
    """Debe fallar si la edad es negativa."""
    with pytest.raises(ValueError, match="La edad no puede ser negativa"):
        service.add_pet("Fido", "Perro", "Mestizo", -1, 1)

def test_add_pet_empty_species(service):
    """Debe fallar si la especie está vacía."""
    with pytest.raises(ValueError, match="La especie es obligatoria"):
        service.add_pet("Fido", "", "Mestizo", 5, 1)

# --- Test de Citas ---

def test_book_appointment_empty_reason(service):
    """Debe fallar si el motivo está vacío."""
    with pytest.raises(ValueError, match="El motivo de la cita es obligatorio"):
        service.book_appointment(1, date.today(), "   ")

# --- Test de Facturación ---

def test_generate_invoice_negative_amount(service):
    """Debe fallar si el monto es negativo o cero."""
    with pytest.raises(ValueError, match="El monto total debe ser mayor a 0"):
        service.generate_invoice(1, -50.00, date.today())
    
    with pytest.raises(ValueError, match="El monto total debe ser mayor a 0"):
        service.generate_invoice(1, 0, date.today())

# --- Test de Reseñas ---

def test_add_review_invalid_rating(service):
    """Debe fallar si el rating está fuera del rango 1-5."""
    with pytest.raises(ValueError, match="La calificación debe ser un entero entre 1 y 5"):
        service.add_review(1, 6, "Muy bien") # 6 es inválido
        
    with pytest.raises(ValueError, match="La calificación debe ser un entero entre 1 y 5"):
        service.add_review(1, 0, "Muy mal") # 0 es inválido