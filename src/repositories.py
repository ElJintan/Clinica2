from typing import List, Optional, Any
from src.interfaces import IRepository
from src.models import Client, Pet, Appointment, MedicalRecord, Invoice, Review # <--- Importar Review
from src.database import DatabaseManager
from src.utils import logger
from datetime import date, datetime # <--- Importar datetime para conversión

# --- Client Repository ---
class ClientRepository(IRepository):
    def __init__(self, db: DatabaseManager):
        self.db = db

    def create(self, client: Client) -> Client:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)", 
                           (client.name, client.email, client.phone))
            client.id = cursor.lastrowid
            return client

    def get_all(self) -> List[Client]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, phone FROM clients")
            rows = cursor.fetchall()
            return [Client(*row) for row in rows]

    def update(self, item: Any) -> bool: 
        client = item 
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE clients SET name=?, email=?, phone=? WHERE id=?", 
                           (client.name, client.email, client.phone, client.id))
            return cursor.rowcount > 0

    def delete(self, item_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id=?", (item_id,))
            return cursor.rowcount > 0
            
    def get_by_id(self, item_id: int) -> Any: 
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, phone FROM clients WHERE id=?", (item_id,))
            row = cursor.fetchone()
            return Client(*row) if row else None


# --- Pet Repository ---
class PetRepository(IRepository):
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create(self, pet: Pet) -> Pet:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pets (name, species, breed, age, client_id) VALUES (?,?,?,?,?)",
                           (pet.name, pet.species, pet.breed, pet.age, pet.client_id))
            pet.id = cursor.lastrowid
            return pet

    def get_all(self) -> List[Pet]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, species, breed, age, client_id FROM pets")
            return [Pet(*row) for row in cursor.fetchall()]
            
    def get_by_client(self, client_id: int) -> List[Pet]:
         with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, species, breed, age, client_id FROM pets WHERE client_id=?", (client_id,))
            return [Pet(*row) for row in cursor.fetchall()]

    def update(self, item: Any) -> bool: 
        pet = item
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE pets SET name=?, species=?, breed=?, age=?, client_id=? WHERE id=?", 
                           (pet.name, pet.species, pet.breed, pet.age, pet.client_id, pet.id))
            return cursor.rowcount > 0 

    def delete(self, item_id: int) -> bool: 
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pets WHERE id=?", (item_id,))
            return cursor.rowcount > 0
            
    def get_by_id(self, item_id: int) -> Any: 
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, species, breed, age, client_id FROM pets WHERE id=?", (item_id,))
            row = cursor.fetchone()
            return Pet(*row) if row else None


# --- Appointment Repository ---
class AppointmentRepository(IRepository):
    def __init__(self, db: DatabaseManager):
        self.db = db

    def create(self, appt: Appointment) -> Appointment:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO appointments (pet_id, date, reason, status) VALUES (?,?,?,?)",
                           (appt.pet_id, appt.date, appt.reason, appt.status))
            appt.id = cursor.lastrowid
            return appt
            
    def get_all(self) -> List[Appointment]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, pet_id, date, reason, status FROM appointments")
            return [Appointment(*row) for row in cursor.fetchall()]

    def update(self, item: Any) -> bool: 
        appt = item
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE appointments SET pet_id=?, date=?, reason=?, status=? WHERE id=?",
                           (appt.pet_id, appt.date, appt.reason, appt.status, appt.id))
            return cursor.rowcount > 0

    def delete(self, item_id: int) -> bool: 
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM appointments WHERE id=?", (item_id,))
            return cursor.rowcount > 0
            
    def get_by_id(self, item_id: int) -> Any: 
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, pet_id, date, reason, status FROM appointments WHERE id=?", (item_id,))
            row = cursor.fetchone()
            return Appointment(*row) if row else None


# --- Medical Record Repository ---
class MedicalRecordRepository(IRepository):
    def __init__(self, db: DatabaseManager):
        self.db = db

    def create(self, record: MedicalRecord) -> MedicalRecord:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO medical_records (appointment_id, diagnosis, treatment, notes) VALUES (?, ?, ?, ?)", 
                           (record.appointment_id, record.diagnosis, record.treatment, record.notes))
            record.id = cursor.lastrowid
            return record

    def get_medical_history_by_pet(self, pet_id: int) -> List[tuple]:
        """Obtiene todos los registros médicos y datos de la cita para una mascota."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    mr.id, a.date, a.reason, mr.diagnosis, mr.treatment, mr.notes
                FROM medical_records mr
                JOIN appointments a ON mr.appointment_id = a.id
                WHERE a.pet_id = ?
                ORDER BY a.date DESC
            """
            cursor.execute(query, (pet_id,))
            return cursor.fetchall() 
            
    def get_all(self) -> List[Any]: return [] 
    def update(self, item: Any) -> bool: return False
    def delete(self, item_id: int) -> bool: return False
    def get_by_id(self, item_id: int) -> Any: return None


# --- Billing Repository ---
class BillingRepository(IRepository):
    def __init__(self, db: DatabaseManager):
        self.db = db

    def create(self, invoice: Invoice) -> Invoice:
        date_to_store = str(invoice.date) 
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO invoices (client_id, date, total_amount, status) VALUES (?, ?, ?, ?)", 
                           (invoice.client_id, date_to_store, invoice.total_amount, invoice.status))
            invoice.id = cursor.lastrowid
            return invoice

    def get_all(self) -> List[Invoice]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, client_id, date, total_amount, status FROM invoices ORDER BY date DESC")
            
            invoices = []
            for row in cursor.fetchall():
                # Conversión de fecha de string a objeto date
                date_obj = datetime.strptime(row[2], '%Y-%m-%d').date()
                invoices.append(Invoice(row[0], row[1], date_obj, row[3], row[4]))
            return invoices

    def update(self, item: Any) -> bool: return False
    def delete(self, item_id: int) -> bool: return False
    def get_by_id(self, item_id: int) -> Any: return None # <--- Implementado

# --- Review Repository (NUEVO) ---
class ReviewRepository(IRepository):
    def __init__(self, db: DatabaseManager):
        self.db = db

    def create(self, review: Review) -> Review:
        date_to_store = str(review.date)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO reviews (client_id, rating, comment, review_date) VALUES (?, ?, ?, ?)", 
                           (review.client_id, review.rating, review.comment, date_to_store))
            review.id = cursor.lastrowid
            return review

    def get_all(self) -> List[Review]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, client_id, rating, comment, review_date FROM reviews ORDER BY review_date DESC")
            reviews = []
            for row in cursor.fetchall():
                # review_date está en el índice 4
                date_obj = datetime.strptime(row[4], '%Y-%m-%d').date()
                reviews.append(Review(row[0], row[1], row[2], row[3], date_obj))
            return reviews
            
    def update(self, item: Any) -> bool: return False
    def delete(self, item_id: int) -> bool: return False
    def get_by_id(self, item_id: int) -> Any: return None