from typing import List, Optional
from src.repositories import ClientRepository, PetRepository, AppointmentRepository, MedicalRecordRepository, BillingRepository, ReviewRepository # <--- AÑADIDO ReviewRepository
from src.models import Client, Pet, Appointment, MedicalRecord, Invoice, Review # <--- AÑADIDO Review
from src.utils import logger, Validators

class ClinicService:
    def __init__(self, client_repo: ClientRepository, pet_repo: PetRepository, appt_repo: AppointmentRepository, mr_repo: MedicalRecordRepository, bill_repo: BillingRepository, review_repo: ReviewRepository): # <--- AÑADIDO review_repo
        self.client_repo = client_repo
        self.pet_repo = pet_repo
        self.appt_repo = appt_repo
        self.mr_repo = mr_repo
        self.bill_repo = bill_repo
        self.review_repo = review_repo # <--- ASIGNADO review_repo

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
        
    def get_pet_by_id(self, pet_id: int) -> Optional[Pet]:
        return self.pet_repo.get_by_id(pet_id)
        
    def update_pet(self, pet: Pet) -> bool:
        """Actualiza una mascota existente, valida la edad."""
        if pet.age < 0:
            raise ValueError("La edad no puede ser negativa")
        return self.pet_repo.update(pet)
        
    def delete_pet(self, pet_id: int):
        self.pet_repo.delete(pet_id)
        
    # --- Appointment Logic ---
    def book_appointment(self, pet_id: int, date_val, reason: str):
        appt = Appointment(id=None, pet_id=pet_id, date=date_val, reason=reason)
        return self.appt_repo.create(appt)

    def update_appointment(self, appt: Appointment):
        """Actualiza una cita existente, valida la fecha."""
        if not Validators.is_valid_date(appt.date):
            raise ValueError("La fecha de la cita no es válida.") 
        return self.appt_repo.update(appt)

    def get_appointment_by_id(self, appt_id: int) -> Optional[Appointment]:
        return self.appt_repo.get_by_id(appt_id)
        
    def list_appointments(self):
        return self.appt_repo.get_all()
        
    def delete_appointment(self, appt_id: int) -> bool:
        """Elimina una cita por su ID."""
        return self.appt_repo.delete(appt_id)
    
    # --- Medical Record Logic ---
    def add_medical_record(self, appointment_id: int, diagnosis: str, treatment: str, notes: Optional[str] = None) -> MedicalRecord:
        """Añade un registro médico a una cita existente."""
        record = MedicalRecord(id=None, appointment_id=appointment_id, diagnosis=diagnosis, treatment=treatment, notes=notes)
        return self.mr_repo.create(record)

    def get_medical_history_by_pet(self, pet_id: int) -> List[tuple]:
        """Obtiene el historial médico completo para una mascota."""
        return self.mr_repo.get_medical_history_by_pet(pet_id)
        
    # --- Billing Logic ---
    def generate_invoice(self, client_id: int, total_amount: float, date_val) -> Invoice:
        """Genera una nueva factura para un cliente."""
        if total_amount <= 0:
            raise ValueError("El monto total debe ser positivo.")
        
        invoice = Invoice(id=None, client_id=client_id, date=date_val, total_amount=total_amount, status="Pendiente")
        return self.bill_repo.create(invoice)

    def list_invoices(self) -> List[Invoice]:
        """Lista todas las facturas."""
        return self.bill_repo.get_all()
        
    # --- Review Logic ---
    def add_review(self, client_id: int, rating: int, comment: Optional[str] = None) -> Review:
        if not 1 <= rating <= 5:
            raise ValueError("La calificación debe estar entre 1 y 5.")
        
        review = Review(id=None, client_id=client_id, rating=rating, comment=comment)
        return self.review_repo.create(review)

    def list_reviews(self) -> List[Review]:
        return self.review_repo.get_all()
    
    # --- Seed Data ---
    def seed_data(self):
        from datetime import date # Importar date localmente para seed
        if not self.list_clients():
            c1 = self.add_client("Juan Perez", "juan@example.com", "555-1234")
            c2 = self.add_client("Maria Lopez", "maria@example.com", "555-5678")
            
            p1 = self.add_pet("Fido", "Perro", "Labrador", 5, c1.id)
            p2 = self.add_pet("Michi", "Gato", "Siames", 2, c2.id)
            
            self.book_appointment(p1.id, date(2023, 12, 1), "Vacunación")
            self.generate_invoice(c1.id, 75.00, date(2023, 12, 1))
            self.add_review(c1.id, 5, "Excelente atención.") # <--- AÑADIDO Review de prueba
            logger.info("Datos de prueba insertados.")