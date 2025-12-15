import pytest
from unittest.mock import Mock, call
from src.services import ClinicService
from src.models import Client, Pet, Appointment, MedicalRecord
from datetime import date

# ----------------------------------------------------
# CLASE DE PRUEBAS
# ----------------------------------------------------

class TestClinicService:
    
    # FIX: Se eliminó @pytest.fixture(autouse=True). 
    # Pytest automáticamente reconoce setup_method para ejecutar antes de CADA test,
    # permitiendo el uso de 'self'.
    def setup_method(self): 
        """Prepara los mocks y el servicio antes de cada prueba."""
        self.mock_client_repo = Mock()
        self.mock_pet_repo = Mock()
        self.mock_appt_repo = Mock()
        self.mock_mr_repo = Mock()
        
        self.service = ClinicService(
            self.mock_client_repo, 
            self.mock_pet_repo, 
            self.mock_appt_repo,
            self.mock_mr_repo
        )
        
        # Objetos de modelo de prueba
        self.client_data = Client(id=1, name="Juan Test", email="juan@test.com", phone="123")
        self.pet_data = Pet(id=10, name="Fido", species="Perro", breed="Labrador", age=5, client_id=1)
        self.appt_data = Appointment(id=100, pet_id=10, date=date(2025, 12, 15), reason="Chequeo", status="Pendiente")
        self.mr_data = MedicalRecord(id=1, appointment_id=100, diagnosis="Gripe felina", treatment="Antibiótico A", notes="Reposo 3 días")

    # ----------------------------------------------------
    # CLIENTE: Pruebas de Cliente (CRUD)
    # ----------------------------------------------------

    def test_add_client_valid(self):
        # Arrange
        self.mock_client_repo.create.return_value = self.client_data
        
        # Act
        result = self.service.add_client("Juan Test", "juan@test.com", "123")
        
        # Assert
        assert result.id == 1
        assert result.email == "juan@test.com"
        self.mock_client_repo.create.assert_called_once()

    def test_add_client_invalid_email_raises_error(self):
        with pytest.raises(ValueError, match="Email inválido"):
            self.service.add_client("Test", "bad-email", "123")

    def test_list_clients_returns_all(self):
        # Arrange
        clients_list = [self.client_data, Client(2, "Ana", "ana@test.com", "456")]
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

        # tests/test_services.py (dentro de la clase TestClinicService)

    def test_delete_client_success(self):
        # Arrange
        client_id_to_delete = 1
        self.mock_client_repo.delete.return_value = True # Simula eliminación exitosa
        
        # Act
        self.service.delete_client(client_id_to_delete)
        
        # Assert
        self.mock_client_repo.delete.assert_called_once_with(client_id_to_delete)

    # --- Nuevas pruebas de actualización de cliente ---
    def test_update_client_valid(self):
        # Arrange
        updated_client = Client(id=1, name="Juan Editado", email="editado@test.com", phone="999")
        self.mock_client_repo.update.return_value = True # Simula éxito
        
        # Act
        result = self.service.update_client(updated_client)
        
        # Assert
        assert result is True
        self.mock_client_repo.update.assert_called_once_with(updated_client)

    def test_update_client_invalid_email_raises_error(self):
        # Arrange
        # Un intento de actualización con un email inválido
        bad_client = Client(id=1, name="Juan Editado", email="mal_email", phone="999")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email inválido"):
            self.service.update_client(bad_client)
            
        # Assert persistence layer was NOT called
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
        # Usamos un objeto Pet simulado con un cambio de nombre y edad
        updated_pet = Pet(id=10, name="Fido Nuevo", species="Perro", breed="Poodle", age=7, client_id=1)
        self.mock_pet_repo.update.return_value = True # Simula que 1 fila fue modificada

        # Act
        result = self.service.update_pet(updated_pet)

        # Assert
        assert result is True
        self.mock_pet_repo.update.assert_called_once_with(updated_pet)
        
  # tests/test_services.py (dentro de la sección # MASCOTA: Pruebas de Mascota)

    def test_update_pet_negative_age_raises_error_on_update(self):
        # Arrange
        # Un intento de actualización con una edad inválida
        bad_pet = Pet(id=10, name="Fido", species="Perro", breed="Poodle", age=-5, client_id=1)

        # Act & Assert
        with pytest.raises(ValueError, match="La edad no puede ser negativa"):
            self.service.update_pet(bad_pet)
        # Se verifica que la capa de persistencia NO fue llamada
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
    # CITA: Pruebas de Cita (Agendar y Listar)
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
        old_appt = self.appt_data # id=100, reason="Chequeo"
        updated_date = date(2026, 1, 15)
        
        # Creamos un objeto Appointment con nuevos datos y el ID existente
        updated_appt = Appointment(
            id=100, 
            pet_id=old_appt.pet_id, 
            date=updated_date, 
            reason="Control Anual", 
            status="Completada" # Nuevo estado
        )
        self.mock_appt_repo.update.return_value = True # Simula éxito

        # Act
        result = self.service.update_appointment(updated_appt)
        
        # Assert
        assert result is True
        self.mock_appt_repo.update.assert_called_once_with(updated_appt)

    def test_update_appointment_invalid_date_raises_error(self):
        # Arrange
        # Una cita con un valor de fecha no válido para la validación
        invalid_appt = Appointment(
            id=100, 
            pet_id=10, 
            date="2025/12/15", # Formato incorrecto, la validación fallará
            reason="Error", 
            status="Pendiente"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="La fecha de la cita no es válida."):
            self.service.update_appointment(invalid_appt)
            
        # Se verifica que la capa de persistencia NO fue llamada
        self.mock_appt_repo.update.assert_not_called()
    
    # Pruebas de eliminación de citas
    def test_delete_appointment_success(self):
        # Arrange
        appt_id_to_delete = 100
        self.mock_appt_repo.delete.return_value = True # Simula eliminación exitosa
        
        # Act
        result = self.service.delete_appointment(appt_id_to_delete)
        
        # Assert
        assert result is True
        self.mock_appt_repo.delete.assert_called_once_with(appt_id_to_delete)
        
    def test_delete_appointment_not_found(self):
        # Arrange
        appt_id_to_delete = 999
        self.mock_appt_repo.delete.return_value = False # Simula que no se encontró
        
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


        # tests/test_services.py (después de las pruebas de Appointment)

    # ----------------------------------------------------
    # HISTORIAL MÉDICO: Pruebas de Registro Médico
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
        
   # tests/test_services.py (dentro de la clase TestClinicService, en la sección de Historial Médico)

    # ... (código anterior)

    def test_get_medical_history_by_pet_returns_list(self):
        # Arrange
        # Simulamos el retorno de la consulta JOIN
        history_data = [
            (2, date(2025, 12, 10), "Chequeo", "Sano", "Ninguno", None),
            # CORRECCIÓN: Quitamos el 0 inicial en el mes y el día (01 -> 1)
            (1, date(2025, 1, 1), "Vacuna", "OK", "Vacuna X", "Sin reacción") 
        ]
        self.mock_mr_repo.get_medical_history_by_pet.return_value = history_data
        
        # Act
        result = self.service.get_medical_history_by_pet(pet_id=10)
        
        # Assert
        assert len(result) == 2
        assert result[0][3] == "Sano" # Diagnóstico del registro más reciente
        self.mock_mr_repo.get_medical_history_by_pet.assert_called_once_with(10)
    # ----------------------------------------------------
    # SEED DATA (Prueba de inicialización de datos)
    # ----------------------------------------------------
    
    def test_seed_data_when_clients_exist(self):
        # Arrange
        # Simulamos que list_clients devuelve algo (ya hay datos)
        self.mock_client_repo.get_all.return_value = [self.client_data] 
        
        # Act
        self.service.seed_data()
        
        # Assert
        # Si ya hay clientes, no se debería llamar a create ni a add_pet/book_appointment
        self.mock_client_repo.get_all.assert_called_once()
        self.mock_client_repo.create.assert_not_called()
        self.mock_pet_repo.create.assert_not_called()
        self.mock_appt_repo.create.assert_not_called()
        
    def test_seed_data_when_clients_do_not_exist(self):
        # Arrange
        # Simulamos que list_clients devuelve una lista vacía (no hay datos)
        self.mock_client_repo.get_all.return_value = [] 
        
        # Simulamos las operaciones de creación de seed_data: Clientes
        c1 = Client(1, "Juan Perez", "juan@example.com", "555-1234")
        c2 = Client(2, "Maria Lopez", "maria@example.com", "555-5678")
        self.mock_client_repo.create.side_effect = [c1, c2]
        
        # Simulamos las operaciones de creación de seed_data: Mascotas (con la corrección de IDs)
        p1_mock = Pet(id=1, name="Fido", species="Perro", breed="Labrador", age=5, client_id=1)
        p2_mock = Pet(id=2, name="Michi", species="Gato", breed="Siames", age=2, client_id=2)
        self.mock_pet_repo.create.side_effect = [p1_mock, p2_mock]
        
        # La creación de cita no necesita un retorno específico para esta prueba
        self.mock_appt_repo.create.return_value = Mock() 
        
        # Act
        self.service.seed_data()
        
        # Assert
        # 1. Se deben haber llamado a client.create 2 veces
        assert self.mock_client_repo.create.call_count == 2
        
        # 2. Se deben haber llamado a pet.create 2 veces (p1 y p2)
        assert self.mock_pet_repo.create.call_count == 2
        
        # 3. Se deben haber llamado a appt.create 1 vez
        self.mock_appt_repo.create.assert_called_once()
        
        # Verificamos que se llamó con el ID de la primera mascota (p1.id)
        assert self.mock_appt_repo.create.call_args[0][0].pet_id == 1