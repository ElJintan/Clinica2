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
        
    def delete_client(self, client_id: int):
        self.client_repo.delete(client_id)

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
        
    def delete_pet(self, pet_id: int):
        self.pet_repo.delete(pet_id)

    # --- Appointment Logic ---
    def book_appointment(self, pet_id: int, date_val, reason: str):
        appt = Appointment(id=None, pet_id=pet_id, date=date_val, reason=reason)
        return self.appt_repo.create(appt)
        
    def list_appointments(self):
        return self.appt_repo.get_all()

    # --- Seed Data ---
    def seed_data(self):
        if not self.list_clients():
            c1 = self.add_client("Juan Perez", "juan@example.com", "555-1234")
            c2 = self.add_client("Maria Lopez", "maria@example.com", "555-5678")
            
            p1 = self.add_pet("Fido", "Perro", "Labrador", 5, c1.id)
            p2 = self.add_pet("Michi", "Gato", "Siames", 2, c2.id)
            
            self.book_appointment(p1.id, "2023-12-01", "Vacunación")
            logger.info("Datos de prueba insertados.")