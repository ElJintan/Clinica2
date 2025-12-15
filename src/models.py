from dataclasses import dataclass
from typing import Optional
from datetime import date

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
    date: date
    reason: str
    status: str = "Pendiente"