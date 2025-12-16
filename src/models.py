from dataclasses import dataclass, field
from typing import Optional
import datetime # Importar el módulo completo para evitar el error de recursión

@dataclass
class Client:
    id: Optional[int]
    name: str
    email: str
    phone: str

@dataclass
class Pet:
    id: Optional[int]
    name: str
    species: str
    breed: str
    age: int
    client_id: int

@dataclass
class Appointment:
    id: Optional[int]
    pet_id: int
    date: datetime.date # Usar datetime.date
    reason: str
    status: str = "Pendiente"

@dataclass
class MedicalRecord:
    id: Optional[int]
    appointment_id: int
    diagnosis: str
    treatment: str
    notes: Optional[str] = None

@dataclass
class Invoice:
    id: Optional[int]
    client_id: int
    date: datetime.date # Usar datetime.date
    total_amount: float
    status: str = "Pendiente"

@dataclass
class Review:
    id: Optional[int]
    client_id: int
    rating: int # 1 to 5
    comment: Optional[str] = None
    date: datetime.date = field(default_factory=datetime.date.today) # Usar datetime.date.today