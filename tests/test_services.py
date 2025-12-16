import pytest
from unittest.mock import Mock, call
from src.services import ClinicService
from src.models import Client, Pet, Appointment, MedicalRecord, Invoice, Review
from datetime import date

class TestClinicService:
    
    def setup_method(self): 
        # Mocks de repositorios
        self.mock_client_repo = Mock()
        self.mock_pet_repo = Mock()
        self.mock_appt_repo = Mock()
        self.mock_mr_repo = Mock()
        self.mock_bill_repo = Mock()
        self.mock_review_repo = Mock()

        # Inyección de dependencias
        self.service = ClinicService(
            self.mock_client_repo, self.mock_pet_repo, self.mock_appt_repo,
            self.mock_mr_repo, self.mock_bill_repo, self.mock_review_repo
        )
        
        # Datos base válidos para reutilizar
        self.valid_client = Client(1, "Juan", "juan@mail.com", "600123456")

    # ----------------------------------------------------------------
    # CLIENTES
    # ----------------------------------------------------------------
    def test_add_client_success(self):
        self.mock_client_repo.create.return_value = self.valid_client
        result = self.service.add_client("Juan", "juan@mail.com", "600123456")
        
        assert result.id == 1
        self.mock_client_repo.create.assert_called_once()

    @pytest.mark.parametrize("name, email, phone, error_msg", [
        ("", "a@b.com", "600123456", "El nombre del cliente no puede estar vacío"),
        ("Juan", "bad-email", "600123456", "Email inválido"),
        ("Juan", "a@b.com", "abc", "Teléfono inválido"),
        ("Juan", "a@b.com", "123", "Teléfono inválido") # Muy corto
    ])
    def test_add_client_validation_errors(self, name, email, phone, error_msg):
        with pytest.raises(ValueError, match=error_msg):
            self.service.add_client(name, email, phone)
        self.mock_client_repo.create.assert_not_called()

    def test_update_client_success(self):
        self.mock_client_repo.update.return_value = True
        self.service.update_client(self.valid_client)
        self.mock_client_repo.update.assert_called_once()

    # ----------------------------------------------------------------
    # MASCOTAS
    # ----------------------------------------------------------------
    def test_add_pet_success(self):
        pet = Pet(10, "Fido", "Perro", "Mix", 5, 1)
        self.mock_pet_repo.create.return_value = pet
        
        result = self.service.add_pet("Fido", "Perro", "Mix", 5, 1)
        assert result.id == 10

    @pytest.mark.parametrize("name, species, age, error_msg", [
        ("", "Perro", 5, "nombre de la mascota es obligatorio"),
        ("Fido", "", 5, "especie es obligatoria"),
        ("Fido", "Perro", -1, "La edad no puede ser negativa")
    ])
    def test_add_pet_validation_errors(self, name, species, age, error_msg):
        with pytest.raises(ValueError, match=error_msg):
            self.service.add_pet(name, species, "Raza", age, 1)
        self.mock_pet_repo.create.assert_not_called()

    # ----------------------------------------------------------------
    # CITAS
    # ----------------------------------------------------------------
    def test_book_appointment_success(self):
        appt_date = date(2025, 12, 25)
        self.mock_appt_repo.create.return_value = Appointment(100, 10, appt_date, "Vacuna", "Pendiente")
        
        result = self.service.book_appointment(10, appt_date, "Vacuna")
        assert result.id == 100

    def test_book_appointment_invalid_data(self):
        with pytest.raises(ValueError, match="El motivo de la cita es obligatorio"):
            self.service.book_appointment(10, date.today(), "")
            
        with pytest.raises(ValueError, match="Fecha inválida"):
             self.service.book_appointment(10, "fecha-texto-mala", "Motivo")

    # ----------------------------------------------------------------
    # FACTURACIÓN (Casos borde de dinero)
    # ----------------------------------------------------------------
    @pytest.mark.parametrize("amount", [0, -10, -0.01])
    def test_generate_invoice_invalid_amount(self, amount):
        with pytest.raises(ValueError, match="El monto total debe ser mayor a 0"):
            self.service.generate_invoice(1, amount, date.today())
        self.mock_bill_repo.create.assert_not_called()

    # ----------------------------------------------------------------
    # RESEÑAS (Límites)
    # ----------------------------------------------------------------
    @pytest.mark.parametrize("rating", [0, 6, 10, -5])
    def test_add_review_invalid_rating(self, rating):
        with pytest.raises(ValueError, match="La calificación debe ser un entero entre 1 y 5"):
            self.service.add_review(1, rating, "Comentario")
            
    def test_add_review_valid_boundary(self):
        # Probar límites válidos (1 y 5)
        self.mock_review_repo.create.return_value = Mock()
        self.service.add_review(1, 1, "Malo")
        self.service.add_review(1, 5, "Bueno")
        assert self.mock_review_repo.create.call_count == 2