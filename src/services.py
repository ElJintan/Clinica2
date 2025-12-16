from typing import List, Optional
from src.repositories import ClientRepository, PetRepository, AppointmentRepository, MedicalRecordRepository, BillingRepository
from src.models import Client, Pet, Appointment, MedicalRecord, Invoice
from src.utils import logger, Validators

class ClinicService:
    def __init__(self, client_repo: ClientRepository, pet_repo: PetRepository, appt_repo: AppointmentRepository, mr_repo: MedicalRecordRepository, bill_repo: BillingRepository):
        self.client_repo = client_repo
        self.pet_repo = pet_repo
        self.appt_repo = appt_repo
        self.mr_repo = mr_repo
        self.bill_repo = bill_repo

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
        
    def delete_pet(self, pet_id: int):
        self.pet_repo.delete(pet_id)
        
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
    
    def get_invoice_by_id(self, invoice_id: int) -> Optional[Invoice]:
        return self.bill_repo.get_by_id(invoice_id)

    def pay_invoice(self, invoice_id: int) -> bool:
        """Marca una factura como 'Pagada'."""
        
        # DEBUG: Print del ID y su tipo justo al inicio del servicio
        print(f"--- DEBUG SERVICE: pay_invoice llamado con ID: {invoice_id}, Tipo: {type(invoice_id)} ---") 

        invoice = self.bill_repo.get_by_id(invoice_id)
        
        if not invoice:
            # Esta línea se ejecuta cuando el repositorio devuelve None
            raise ValueError(f"Factura ID {invoice_id} no encontrada.")
            
        if invoice.status == "Pagada":
            # Si ya está pagada, consideramos que la operación es exitosa (idempotente)
            return True 
            
        invoice.status = "Pagada"
        
        # Llama al repositorio para actualizar el estado
        return self.bill_repo.update(invoice)


    def list_invoices(self) -> List[Invoice]:
        """Lista todas las facturas."""
        return self.bill_repo.get_all()
    
    # --- Seed Data ---
    def seed_data(self):
        if not self.list_clients():
            c1 = self.add_client("Juan Perez", "juan@example.com", "555-1234")
            c2 = self.add_client("Maria Lopez", "maria@example.com", "555-5678")
            
            p1 = self.add_pet("Fido", "Perro", "Labrador", 5, c1.id)
            p2 = self.add_pet("Michi", "Gato", "Siames", 2, c2.id)
            
            self.book_appointment(p1.id, "2023-12-01", "Vacunación")
            logger.info("Datos de prueba insertados.")