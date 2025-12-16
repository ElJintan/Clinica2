import pytest
from src.utils import Validators

class TestValidators:
    
    # --- EMAIL ---
    @pytest.mark.parametrize("email", [
        "usuario@dominio.com",
        "nombre.apellido@empresa.co.uk",
        "123@numeros.com"
    ])
    def test_email_valid(self, email):
        assert Validators.is_valid_email(email) is True

    @pytest.mark.parametrize("email", [
        "sinarroba.com",
        "usuario@dominio", # Falta TLD
        "@dominio.com",
        "usuario@.com",
        "", 
        None
    ])
    def test_email_invalid(self, email):
        assert Validators.is_valid_email(email) is False

    # --- TELÉFONO ---
    @pytest.mark.parametrize("phone", [
        "600123456", 
        "+34600123456",
        "1234567" # Mínimo 7
    ])
    def test_phone_valid(self, phone):
        assert Validators.is_valid_phone(phone) is True

    @pytest.mark.parametrize("phone", [
        "123", # Muy corto
        "abcdefghi", # Letras
        "600-123-456", # Guiones (tu regex actual solo admite dígitos)
        "", 
        None
    ])
    def test_phone_invalid(self, phone):
        assert Validators.is_valid_phone(phone) is False

    # --- NÚMEROS Y TEXTO ---
    def test_is_not_empty(self):
        assert Validators.is_not_empty("Hola") is True
        assert Validators.is_not_empty("   ") is False
        assert Validators.is_not_empty("") is False
        assert Validators.is_not_empty(None) is False

    def test_positive_numbers(self):
        assert Validators.is_positive_number(10) is True
        assert Validators.is_positive_number(0.1) is True
        assert Validators.is_positive_number(0) is False # Debe ser mayor a 0
        assert Validators.is_positive_number(-5) is False

    def test_valid_date(self):
        assert Validators.is_valid_date("2025-12-31") is True
        assert Validators.is_valid_date("2025-02-30") is False # Fecha imposible (febrero 30)
        assert Validators.is_valid_date("texto") is False