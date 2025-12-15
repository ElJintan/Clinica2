from typing import List
from src.repositories import ClientRepository, PetRepository, AppointmentRepository
from src.models import Client, Pet, Appointment
from src.utils import logger, Validators

class ClinicService:
    def __init__(self, client_repo: ClientRepository, pet_repo: PetRepository, appt_repo: AppointmentRepository):
        self.client_repo = client_repo
        self.pet_repo = pet_repo
        self.appt_repo = appt_repo

    # --- Client Logic ---
    def add_client(self, name: str, email: str, phone: str) -> Client:
        if not Validators.is_valid_email(email):
            raise ValueError("Email inválido")
        client = Client(id=None, name=name, email=email, phone=phone)
        try:
            new_client = self.client_repo.create(client)
            logger.info(f"Cliente creado: {new_client.id}")
            return new_client
        except Exception as e:
            logger.error(f"Error creando cliente: {e}")
            raise

    def list_clients(self) -> List[Client]:
        return self.client_repo.get_all()
        
    def update_client(self, client: Client) -> bool:
        """Actualiza un cliente existente, valida el email."""
        if not Validators.is_valid_email(client.email):
            raise ValueError("Email inválido")
        try:
            return self.client_repo.update(client)
        except Exception as e:
            logger.error(f"Error actualizando cliente: {e}")
            raise
        
    def delete_client(self, client_id: int):
        self.client_repo.delete(client_id)
# ...

    # --- Pet Logic ---
    def add_pet(self, name: str, species: str, breed: str, age: int, client_id: int) -> Pet:
        if age < 0:
            raise ValueError("La edad no puede ser negativa")
        pet = Pet(id=None, name=name, species=species, breed=breed, age=age, client_id=client_id)
        return self.pet_repo.create(pet)

    def list_pets(self) -> List[Pet]:
        return self.pet_repo.get_all()

    def list_pets_by_client(self, client_id: int) -> List[Pet]:
        return self.pet_repo.get_by_client(client_id)
    

    def list_pets_by_client(self, client_id: int) -> List[Pet]:
        return self.pet_repo.get_by_client(client_id)
        
    def update_pet(self, pet: Pet) -> bool:
        """Actualiza una mascota existente, valida la edad."""
        if pet.age < 0:
            raise ValueError("La edad no puede ser negativa")
        # La validación de que el cliente_id existe podría ir aquí, pero por simplicidad,
        # confiamos en la FK de la BD y en que el Pet ya tiene un ID asignado.
        return self.pet_repo.update(pet)
        
    def delete_pet(self, pet_id: int):
        self.pet_repo.delete(pet_id)
        
    def delete_pet(self, pet_id: int):
        self.pet_repo.delete(pet_id)

    # src/services.py (dentro de la clase ClinicService, después de book_appointment)

    # --- Appointment Logic ---
    def book_appointment(self, pet_id: int, date_val, reason: str):
        appt = Appointment(id=None, pet_id=pet_id, date=date_val, reason=reason)
        return self.appt_repo.create(appt)

    def update_appointment(self, appt: Appointment):
        """Actualiza una cita existente, valida la fecha."""
        if not Validators.is_valid_date(appt.date):
            # La validación se aplica convirtiendo el objeto date a string (YYYY-MM-DD)
            raise ValueError("La fecha de la cita no es válida.") 
        return self.appt_repo.update(appt)
        
    # src/services.py (dentro de la clase ClinicService, después de list_appointments)

    def list_appointments(self):
        return self.appt_repo.get_all()
        
    def delete_appointment(self, appt_id: int) -> bool:
        """Elimina una cita por su ID."""
        return self.appt_repo.delete(appt_id)
        
    # --- Seed Data ---
    def seed_data(self):
        if not self.list_clients():
            c1 = self.add_client("Juan Perez", "juan@example.com", "555-1234")
            c2 = self.add_client("Maria Lopez", "maria@example.com", "555-5678")
            
            p1 = self.add_pet("Fido", "Perro", "Labrador", 5, c1.id)
            p2 = self.add_pet("Michi", "Gato", "Siames", 2, c2.id)
            
            self.book_appointment(p1.id, "2023-12-01", "Vacunación")
            logger.info("Datos de prueba insertados.")