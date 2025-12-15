import pytest
from unittest.mock import Mock
from src.services import ClinicService
from src.models import Client

# Test Unitario usando Mocks para aislar la base de datos
def test_add_client_valid():
    # Arrange
    mock_client_repo = Mock()
    mock_pet_repo = Mock()
    mock_appt_repo = Mock()
    
    # Simulamos que el repo devuelve el cliente con ID 1
    mock_client_repo.create.return_value = Client(1, "Test", "test@test.com", "123")
    
    service = ClinicService(mock_client_repo, mock_pet_repo, mock_appt_repo)
    
    # Act
    result = service.add_client("Test", "test@test.com", "123")
    
    # Assert
    assert result.id == 1
    assert result.email == "test@test.com"
    mock_client_repo.create.assert_called_once()

def test_add_client_invalid_email():
    service = ClinicService(Mock(), Mock(), Mock())
    with pytest.raises(ValueError):
        service.add_client("Test", "bad-email", "123")