from typing import List, Optional, Any  # <--- Aquí faltaba añadir 'Any'
from src.interfaces import IRepository
from src.models import Client, Pet, Appointment
from src.database import DatabaseManager

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

    def update(self, client: Client) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE clients SET name=?, email=?, phone=? WHERE id=?", 
                           (client.name, client.email, client.phone, client.id))
            return cursor.rowcount > 0

    def delete(self, id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id=?", (id,))
            return cursor.rowcount > 0
            
    def get_by_id(self, id: int) -> Optional[Client]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, phone FROM clients WHERE id=?", (id,))
            row = cursor.fetchone()
            return Client(*row) if row else None
    
    # Para cumplir con la interfaz, añadimos este método genérico aunque usemos get_by_id específico arriba
    def get_by_id_generic(self, item_id: int) -> Any:
        return self.get_by_id(item_id)


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

    # src/repositories.py (dentro de la clase PetRepository)

    def update(self, pet: Pet) -> bool: 
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE pets SET name=?, species=?, breed=?, age=?, client_id=? WHERE id=?", 
                           (pet.name, pet.species, pet.breed, pet.age, pet.client_id, pet.id))
            return cursor.rowcount > 0

    def delete(self, item_id: int) -> bool: 
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM pets WHERE id=?", (item_id,))
            return True
            
    def get_by_id(self, item_id: int) -> Any: 
        pass

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
            
    # src/repositories.py (dentro de la clase AppointmentRepository)

    # ... (código anterior)

    def get_all(self) -> List[Appointment]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, pet_id, date, reason, status FROM appointments")
            return [Appointment(*row) for row in cursor.fetchall()]

    def update(self, appt: Appointment) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE appointments SET pet_id=?, date=?, reason=?, status=? WHERE id=?",
                           (appt.pet_id, appt.date, appt.reason, appt.status, appt.id))
            return cursor.rowcount > 0
            
    def delete(self, item_id: int) -> bool:
        """Elimina una cita por su ID."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Ejecuta la sentencia DELETE
            cursor.execute("DELETE FROM appointments WHERE id=?", (item_id,))
            # Devuelve True si se eliminó al menos una fila (rowcount > 0)
            return cursor.rowcount > 0
            
    def get_by_id(self, item_id: int) -> Any: pass