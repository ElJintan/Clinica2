from typing import List, Optional
from src.repositories import ClientRepository, PetRepository, AppointmentRepository, MedicalRecordRepository, BillingRepository, ReviewRepository
from src.models import Client, Pet, Appointment, MedicalRecord, Invoice, Review
from src.utils import logger, Validators
import bcrypt
from src.repositories import UserRepository
from src.models import User

class ClinicService:
    def __init__(self, client_repo: ClientRepository, pet_repo: PetRepository, appt_repo: AppointmentRepository, mr_repo: MedicalRecordRepository, bill_repo: BillingRepository, review_repo: ReviewRepository):
        self.client_repo = client_repo
        self.pet_repo = pet_repo
        self.appt_repo = appt_repo
        self.mr_repo = mr_repo
        self.bill_repo = bill_repo
        self.review_repo = review_repo

    # --- Client Logic ---
    def add_client(self, name: str, email: str, phone: str) -> Client:
        # Validaciones
        if not Validators.is_not_empty(name):
            raise ValueError("El nombre del cliente no puede estar vacío.")
        if not Validators.is_valid_email(email):
            raise ValueError("Email inválido.")
        if not Validators.is_valid_phone(phone):
            raise ValueError("Teléfono inválido. Debe contener solo números (7-15 dígitos).")

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
        if not Validators.is_not_empty(client.name):
            raise ValueError("El nombre no puede estar vacío.")
        if not Validators.is_valid_email(client.email):
            raise ValueError("Email inválido.")
        if not Validators.is_valid_phone(client.phone):
            raise ValueError("Teléfono inválido.")
            
        try:
            return self.client_repo.update(client)
        except Exception as e:
            logger.error(f"Error actualizando cliente: {e}")
            raise
        
    def delete_client(self, client_id: int):
        self.client_repo.delete(client_id)

    # --- Pet Logic ---
    def add_pet(self, name: str, species: str, breed: str, age: int, client_id: int) -> Pet:
        if not Validators.is_not_empty(name):
            raise ValueError("El nombre de la mascota es obligatorio.")
        if not Validators.is_not_empty(species):
            raise ValueError("La especie es obligatoria.")
        if not Validators.is_non_negative(age):
            raise ValueError("La edad no puede ser negativa.")
            
        pet = Pet(id=None, name=name, species=species, breed=breed, age=age, client_id=client_id)
        return self.pet_repo.create(pet)

    def list_pets(self) -> List[Pet]:
        return self.pet_repo.get_all()

    def list_pets_by_client(self, client_id: int) -> List[Pet]:
        return self.pet_repo.get_by_client(client_id)
        
    def get_pet_by_id(self, pet_id: int) -> Optional[Pet]:
        return self.pet_repo.get_by_id(pet_id)
        
    def update_pet(self, pet: Pet) -> bool:
        if not Validators.is_not_empty(pet.name):
            raise ValueError("El nombre de la mascota es obligatorio.")
        if pet.age < 0:
            raise ValueError("La edad no puede ser negativa.")
        return self.pet_repo.update(pet)
        
    def delete_pet(self, pet_id: int):
        self.pet_repo.delete(pet_id)
        
    # --- Appointment Logic ---
    def book_appointment(self, pet_id: int, date_val, reason: str):
        if not Validators.is_valid_date(date_val):
            raise ValueError("Fecha inválida.")
        if not Validators.is_not_empty(reason):
            raise ValueError("El motivo de la cita es obligatorio.")

        appt = Appointment(id=None, pet_id=pet_id, date=date_val, reason=reason)
        return self.appt_repo.create(appt)

    def update_appointment(self, appt: Appointment):
        if not Validators.is_valid_date(appt.date):
            raise ValueError("La fecha de la cita no es válida.") 
        if not Validators.is_not_empty(appt.reason):
            raise ValueError("El motivo es obligatorio.")
        return self.appt_repo.update(appt)

    def get_appointment_by_id(self, appt_id: int) -> Optional[Appointment]:
        return self.appt_repo.get_by_id(appt_id)
        
    def list_appointments(self):
        return self.appt_repo.get_all()
        
    def delete_appointment(self, appt_id: int) -> bool:
        return self.appt_repo.delete(appt_id)
    
    # --- Medical Record Logic ---
    def add_medical_record(self, appointment_id: int, diagnosis: str, treatment: str, notes: Optional[str] = None) -> MedicalRecord:
        if not Validators.is_not_empty(diagnosis):
            raise ValueError("El diagnóstico no puede estar vacío.")
        if not Validators.is_not_empty(treatment):
            raise ValueError("El tratamiento no puede estar vacío.")
            
        record = MedicalRecord(id=None, appointment_id=appointment_id, diagnosis=diagnosis, treatment=treatment, notes=notes)
        return self.mr_repo.create(record)

    def get_medical_history_by_pet(self, pet_id: int) -> List[tuple]:
        return self.mr_repo.get_medical_history_by_pet(pet_id)
        
    # --- Billing Logic ---
    def generate_invoice(self, client_id: int, total_amount: float, date_val) -> Invoice:
        if not Validators.is_positive_number(total_amount):
            raise ValueError("El monto total debe ser mayor a 0.")
        if not Validators.is_valid_date(date_val):
            raise ValueError("Fecha inválida.")
        
        invoice = Invoice(id=None, client_id=client_id, date=date_val, total_amount=total_amount, status="Pendiente")
        return self.bill_repo.create(invoice)

    def list_invoices(self) -> List[Invoice]:
        return self.bill_repo.get_all()
        
    # --- Review Logic ---
    def add_review(self, client_id: int, rating: int, comment: Optional[str] = None) -> Review:
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            raise ValueError("La calificación debe ser un entero entre 1 y 5.")
        
        review = Review(id=None, client_id=client_id, rating=rating, comment=comment)
        return self.review_repo.create(review)

    def list_reviews(self) -> List[Review]:
        return self.review_repo.get_all()
    
    
# LOGIN

# --- Añadir nueva clase AuthService ---

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register_user(self, username: str, password: str, role: str = "admin") -> User:
        if self.user_repo.get_by_username(username):
            raise ValueError("El usuario ya existe.")
        
        # Hash password (SOLID: Security logic encapsulated here)
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(id=None, username=username, password_hash=hashed, role=role)
        return self.user_repo.create(user)

    def login(self, username: str, password: str) -> Optional[User]:
        user = self.user_repo.get_by_username(username)
        if not user:
            return None
        
        # Verificar contraseña
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return user
        return None
    
    def create_admin_if_not_exists(self):
        """Helper para crear el usuario inicial"""
        if not self.user_repo.get_by_username("admin"):
            self.register_user("admin", "admin123")
            logger.info("Usuario admin creado por defecto.")