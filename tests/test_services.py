import pytest
from unittest.mock import Mock, call
from src.services import ClinicService
from src.models import Client, Pet, Appointment, MedicalRecord, Invoice, Review
from datetime import date

# ----------------------------------------------------
# CLASE DE PRUEBAS
# ----------------------------------------------------

class TestClinicService:
    
    def setup_method(self): 
        """Prepara los mocks y el servicio antes de cada prueba."""
        self.mock_client_repo = Mock()
        self.mock_pet_repo = Mock()
        self.mock_appt_repo = Mock()
        self.mock_mr_repo = Mock()
        self.mock_bill_repo = Mock()
        self.mock_review_repo = Mock()

        self.service = ClinicService(
            self.mock_client_repo, 
            self.mock_pet_repo, 
            self.mock_appt_repo,
            self.mock_mr_repo,
            self.mock_bill_repo,
            self.mock_review_repo
        )
        
        # Objetos de modelo de prueba con DATOS VÁLIDOS
        # Nota: El teléfono "123" fallaba, ahora usamos "5551234" (7 dígitos)
        self.client_data = Client(id=1, name="Juan Test", email="juan@test.com", phone="5551234")
        self.pet_data = Pet(id=10, name="Fido", species="Perro", breed="Labrador", age=5, client_id=1)
        self.appt_data = Appointment(id=100, pet_id=10, date=date(2025, 12, 15), reason="Chequeo", status="Pendiente")
        self.mr_data = MedicalRecord(id=1, appointment_id=100, diagnosis="Gripe felina", treatment="Antibiótico A", notes="Reposo 3 días")
        self.invoice_data = Invoice(id=500, client_id=1, date=date(2025, 12, 16), total_amount=45.50, status="Pendiente")
        self.review_data = Review(id=1, client_id=1, rating=5, comment="Excelente servicio", date=date(2025, 12, 16))

    # ----------------------------------------------------
    # CLIENTE: Pruebas de Cliente (CRUD)
    # ----------------------------------------------------

    def test_add_client_valid(self):
        # Arrange
        self.mock_client_repo.create.return_value = self.client_data
        
        # Act
        # Usamos un teléfono válido (mínimo 7 dígitos)
        result = self.service.add_client("Juan Test", "juan@test.com", "5551234")
        
        # Assert
        assert result.id == 1
        assert result.email == "juan@test.com"
        self.mock_client_repo.create.assert_called_once()

    def test_add_client_invalid_email_raises_error(self):
        with pytest.raises(ValueError, match="Email inválido"):
            self.service.add_client("Test", "bad-email", "5551234")

    def test_list_clients_returns_all(self):
        # Arrange
        clients_list = [self.client_data, Client(2, "Ana", "ana@test.com", "5556789")]
        self.mock_client_repo.get_all.return_value = clients_list
        
        # Act
        result = self.service.list_clients()
        
        # Assert
        assert len(result) == 2
        assert result[0].name == "Juan Test"
        self.mock_client_repo.get_all.assert_called_once()

    def test_delete_client_success(self):
        # Arrange
        client_id_to_delete = 1
        self.mock_client_repo.delete.return_value = True 
        
        # Act
        self.service.delete_client(client_id_to_delete)
        
        # Assert
        self.mock_client_repo.delete.assert_called_once_with(client_id_to_delete)

    def test_update_client_valid(self):
        # Arrange
        # Usamos teléfono válido en la actualización también
        updated_client = Client(id=1, name="Juan Editado", email="editado@test.com", phone="5559876")
        self.mock_client_repo.update.return_value = True 
        
        # Act
        result = self.service.update_client(updated_client)
        
        # Assert
        assert result is True
        self.mock_client_repo.update.assert_called_once_with(updated_client)

    def test_update_client_invalid_email_raises_error(self):
        # Arrange
        bad_client = Client(id=1, name="Juan Editado", email="mal_email", phone="5559876")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email inválido"):
            self.service.update_client(bad_client)
            
        self.mock_client_repo.update.assert_not_called()

    # ----------------------------------------------------
    # MASCOTA: Pruebas de Mascota (CRUD)
    # ----------------------------------------------------

    def test_add_pet_valid(self):
        # Arrange
        self.mock_pet_repo.create.return_value = self.pet_data
        
        # Act
        result = self.service.add_pet(
            name=self.pet_data.name,
            species=self.pet_data.species,
            breed=self.pet_data.breed,
            age=self.pet_data.age,
            client_id=self.pet_data.client_id
        )
        
        # Assert
        assert result.id == 10
        assert result.species == "Perro"
        self.mock_pet_repo.create.assert_called_once()
        
    def test_add_pet_negative_age_raises_error(self):
        # Act & Assert
        with pytest.raises(ValueError, match="La edad no puede ser negativa"):
            self.service.add_pet("Fido", "Perro", "Labrador", -1, 1)

    def test_update_pet_valid(self):
        # Arrange
        updated_pet = Pet(id=10, name="Fido Nuevo", species="Perro", breed="Poodle", age=7, client_id=1)
        self.mock_pet_repo.update.return_value = True 

        # Act
        result = self.service.update_pet(updated_pet)

        # Assert
        assert result is True
        self.mock_pet_repo.update.assert_called_once_with(updated_pet)
        
    def test_update_pet_negative_age_raises_error_on_update(self):
        # Arrange
        bad_pet = Pet(id=10, name="Fido", species="Perro", breed="Poodle", age=-5, client_id=1)

        # Act & Assert
        with pytest.raises(ValueError, match="La edad no puede ser negativa"):
            self.service.update_pet(bad_pet)
        self.mock_pet_repo.update.assert_not_called()
        
    # --- PRUEBAS DE BÚSQUEDA POR ID (PET) ---
    def test_get_pet_by_id_found(self):
        # Arrange
        self.mock_pet_repo.get_by_id.return_value = self.pet_data
        
        # Act
        result = self.service.get_pet_by_id(10)
        
        # Assert
        assert result == self.pet_data
        self.mock_pet_repo.get_by_id.assert_called_once_with(10)
        
    def test_get_pet_by_id_not_found(self):
        # Arrange
        self.mock_pet_repo.get_by_id.return_value = None
        
        # Act
        result = self.service.get_pet_by_id(999)
        
        # Assert
        assert result is None
        self.mock_pet_repo.get_by_id.assert_called_once_with(999)

    def test_list_pets_by_client_returns_filtered_list(self):
        # Arrange
        pet_list = [self.pet_data, Pet(11, "Mishi", "Gato", "Siamés", 2, 1)]
        self.mock_pet_repo.get_by_client.return_value = pet_list
        client_id = 1
        
        # Act
        result = self.service.list_pets_by_client(client_id)
        
        # Assert
        assert len(result) == 2
        assert all(p.client_id == client_id for p in result)
        self.mock_pet_repo.get_by_client.assert_called_once_with(client_id)

    def test_delete_pet_success(self):
        # Arrange
        pet_id_to_delete = 10
        self.mock_pet_repo.delete.return_value = True
        
        # Act
        self.service.delete_pet(pet_id_to_delete)
        
        # Assert
        self.mock_pet_repo.delete.assert_called_once_with(pet_id_to_delete)


    # ----------------------------------------------------
    # CITA: Pruebas de Cita
    # ----------------------------------------------------

    def test_book_appointment_success(self):
        # Arrange
        test_date = date(2025, 1, 1)
        self.mock_appt_repo.create.return_value = Appointment(
            id=200, 
            pet_id=self.pet_data.id, 
            date=test_date, 
            reason="Control"
        )
        
        # Act
        result = self.service.book_appointment(self.pet_data.id, test_date, "Control")
        
        # Assert
        assert result.id == 200
        assert result.reason == "Control"
        assert result.status == "Pendiente"
        self.mock_appt_repo.create.assert_called_once()
        
    def test_list_appointments_returns_all(self):
        # Arrange
        appt_list = [self.appt_data, Appointment(101, 11, date(2025, 12, 16), "Vacuna", "Pendiente")]
        self.mock_appt_repo.get_all.return_value = appt_list
        
        # Act
        result = self.service.list_appointments()
        
        # Assert
        assert len(result) == 2
        assert result[0].pet_id == 10
        self.mock_appt_repo.get_all.assert_called_once()

    def test_update_appointment_success(self):
        # Arrange
        old_appt = self.appt_data 
        updated_date = date(2026, 1, 15)
        
        updated_appt = Appointment(
            id=100, 
            pet_id=old_appt.pet_id, 
            date=updated_date, 
            reason="Control Anual", 
            status="Completada" 
        )
        self.mock_appt_repo.update.return_value = True 

        # Act
        result = self.service.update_appointment(updated_appt)
        
        # Assert
        assert result is True
        self.mock_appt_repo.update.assert_called_once_with(updated_appt)

    def test_update_appointment_invalid_date_raises_error(self):
        # Arrange
        invalid_appt = Appointment(
            id=100, 
            pet_id=10, 
            date="2025/12/15",
            reason="Error", 
            status="Pendiente"
        )
        
        # Act & Assert
        # Asegúrate de que este mensaje coincida con el de src/services.py
        with pytest.raises(ValueError, match="La fecha de la cita no es válida."):
            self.service.update_appointment(invalid_appt)
            
        self.mock_appt_repo.update.assert_not_called()
    
    def test_delete_appointment_success(self):
        # Arrange
        appt_id_to_delete = 100
        self.mock_appt_repo.delete.return_value = True 
        
        # Act
        result = self.service.delete_appointment(appt_id_to_delete)
        
        # Assert
        assert result is True
        self.mock_appt_repo.delete.assert_called_once_with(appt_id_to_delete)
        
    def test_delete_appointment_not_found(self):
        # Arrange
        appt_id_to_delete = 999
        self.mock_appt_repo.delete.return_value = False 
        
        # Act
        result = self.service.delete_appointment(appt_id_to_delete)
        
        # Assert
        assert result is False
        self.mock_appt_repo.delete.assert_called_once_with(appt_id_to_delete)

    def test_get_appointment_by_id_found(self):
        # Arrange
        self.mock_appt_repo.get_by_id.return_value = self.appt_data
        
        # Act
        result = self.service.get_appointment_by_id(100)
        
        # Assert
        assert result == self.appt_data
        self.mock_appt_repo.get_by_id.assert_called_once_with(100)
        
    def test_get_appointment_by_id_not_found(self):
        # Arrange
        self.mock_appt_repo.get_by_id.return_value = None
        
        # Act
        result = self.service.get_appointment_by_id(999)
        
        # Assert
        assert result is None
        self.mock_appt_repo.get_by_id.assert_called_once_with(999)


    # ----------------------------------------------------
    # HISTORIAL MÉDICO
    # ----------------------------------------------------

    def test_add_medical_record_success(self):
        # Arrange
        record_to_return = MedicalRecord(id=1, appointment_id=100, diagnosis="Gripe canina", treatment="Vacuna anual", notes="OK")
        self.mock_mr_repo.create.return_value = record_to_return
        
        # Act
        result = self.service.add_medical_record(
            appointment_id=100, 
            diagnosis="Gripe canina", 
            treatment="Vacuna anual", 
            notes="OK"
        )
        
        # Assert
        assert result.id == 1
        assert result.diagnosis == "Gripe canina"
        self.mock_mr_repo.create.assert_called_once()
        
    def test_get_medical_history_by_pet_returns_list(self):
        # Arrange
        history_data = [
            (2, date(2025, 12, 10), "Chequeo", "Sano", "Ninguno", None),
            (1, date(2025, 1, 1), "Vacuna", "OK", "Vacuna X", "Sin reacción") 
        ]
        self.mock_mr_repo.get_medical_history_by_pet.return_value = history_data
        
        # Act
        result = self.service.get_medical_history_by_pet(pet_id=10)
        
        # Assert
        assert len(result) == 2
        assert result[0][3] == "Sano" 
        self.mock_mr_repo.get_medical_history_by_pet.assert_called_once_with(10)

    # ----------------------------------------------------
    # FACTURACIÓN
    # ----------------------------------------------------

    def test_generate_invoice_success(self):
        # Arrange
        test_date = date(2025, 12, 16)
        self.mock_bill_repo.create.return_value = self.invoice_data
        
        # Act
        result = self.service.generate_invoice(
            client_id=1, 
            total_amount=45.50, 
            date_val=test_date
        )
        
        # Assert
        assert result.id == 500
        assert result.total_amount == 45.50
        assert result.status == "Pendiente"
        self.mock_bill_repo.create.assert_called_once()
        
    def test_generate_invoice_negative_amount_raises_error(self):
        # Act & Assert
        # Actualizado para coincidir con "mayor a 0" o "positivo"
        # Si usaste mi código anterior, el mensaje es "El monto total debe ser mayor a 0."
        with pytest.raises(ValueError, match="El monto total debe ser mayor a 0"):
            self.service.generate_invoice(client_id=1, total_amount=-10.00, date_val=date(2025, 1, 1))
        self.mock_bill_repo.create.assert_not_called()

    def test_list_invoices_returns_all(self):
        # Arrange
        invoice_list = [self.invoice_data, Invoice(id=501, client_id=2, date=date(2025, 12, 15), total_amount=120.00, status="Pendiente")]
        self.mock_bill_repo.get_all.return_value = invoice_list
        
        # Act
        result = self.service.list_invoices()
        
        # Assert
        assert len(result) == 2
        assert result[0].client_id == 1
        self.mock_bill_repo.get_all.assert_called_once()

    # ----------------------------------------------------
    # RESEÑAS
    # ----------------------------------------------------

    def test_add_review_valid(self):
        # Arrange
        self.mock_review_repo.create.return_value = self.review_data
        
        # Act
        result = self.service.add_review(
            client_id=1, 
            rating=5, 
            comment="Excelente servicio"
        )
        
        # Assert
        assert result.id == 1
        assert result.rating == 5
        self.mock_review_repo.create.assert_called_once()
        
    def test_add_review_invalid_rating_raises_error(self):
        # Act & Assert
        # Actualizado para coincidir con el mensaje del código "entero entre 1 y 5"
        with pytest.raises(ValueError, match="La calificación debe ser un entero entre 1 y 5"):
            self.service.add_review(client_id=1, rating=6)
        self.mock_review_repo.create.assert_not_called()

    def test_list_reviews_returns_all(self):
        # Arrange
        review_list = [self.review_data, Review(id=2, client_id=2, rating=3, comment="Aceptable", date=date(2025, 12, 15))]
        self.mock_review_repo.get_all.return_value = review_list
        
        # Act
        result = self.service.list_reviews()
        
        # Assert
        assert len(result) == 2
        assert result[1].rating == 3
        self.mock_review_repo.get_all.assert_called_once()
    
    # ----------------------------------------------------
    # SEED DATA
    # ----------------------------------------------------
    
    def test_seed_data_when_clients_exist(self):
        # Arrange
        self.mock_client_repo.get_all.return_value = [self.client_data] 
        
        # Act
        self.service.seed_data()
        
        # Assert
        self.mock_client_repo.get_all.assert_called_once()
        self.mock_client_repo.create.assert_not_called()
        
    def test_seed_data_when_clients_do_not_exist(self):
        # Arrange
        self.mock_client_repo.get_all.return_value = [] 
        
        # Retornos simulados para cada llamada a create
        c1 = Client(1, "Juan Perez", "juan@example.com", "5551234")
        c2 = Client(2, "Maria Lopez", "maria@example.com", "5555678")
        self.mock_client_repo.create.side_effect = [c1, c2]
        
        p1_mock = Pet(id=1, name="Fido", species="Perro", breed="Labrador", age=5, client_id=1)
        p2_mock = Pet(id=2, name="Michi", species="Gato", breed="Siames", age=2, client_id=2)
        self.mock_pet_repo.create.side_effect = [p1_mock, p2_mock]
        
        self.mock_appt_repo.create.return_value = Mock() 
        self.mock_bill_repo.create.return_value = Mock() 
        self.mock_review_repo.create.return_value = Mock()
        
        # Act
        self.service.seed_data()
        
        # Assert
        assert self.mock_client_repo.create.call_count == 2
        assert self.mock_pet_repo.create.call_count == 2
        self.mock_appt_repo.create.assert_called_once()
        self.mock_bill_repo.create.assert_called_once()
        self.mock_review_repo.create.assert_called_once()