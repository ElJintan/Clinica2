# src/seeder.py
from datetime import date, timedelta
import random
from src.repositories import (
    ClientRepository, PetRepository, AppointmentRepository, 
    MedicalRecordRepository, BillingRepository, ReviewRepository
)
from src.models import Client, Pet, Appointment, MedicalRecord, Invoice, Review
from src.utils import logger

class DataSeeder:
    """Clase encargada exclusivamente de poblar la base de datos con datos iniciales."""
    
    def __init__(self, client_repo: ClientRepository, pet_repo: PetRepository, 
                 appt_repo: AppointmentRepository, mr_repo: MedicalRecordRepository, 
                 bill_repo: BillingRepository, review_repo: ReviewRepository):
        self.client_repo = client_repo
        self.pet_repo = pet_repo
        self.appt_repo = appt_repo
        self.mr_repo = mr_repo
        self.bill_repo = bill_repo
        self.review_repo = review_repo

    def seed(self):
        """Ejecuta la carga de datos solo si no hay clientes registrados."""
        if self.client_repo.get_all():
            logger.info("La base de datos ya contiene datos. Se omite el seeding.")
            return

        logger.info("Iniciando carga de datos masiva...")

        # --- 1. Clientes ---
        clients_data = [
            ("Ana García", "ana.garcia@email.com", "600123456"),
            ("Carlos Ruiz", "carlos.ruiz@email.com", "600987654"),
            ("Elena M.", "elena.vetlover@email.com", "666777888"),
            ("Luis Torres", "luis.t@email.com", "611223344"),
            ("Marta Díaz", "marta.d@email.com", "699887766"),
            ("Pedro P.", "pedro.p@email.com", "655443322"),
            ("Sofia L.", "sofia.l@email.com", "644112233"),
            ("Jorge B.", "jorge.b@email.com", "633221144"),
        ]
        
        clients = []
        for name, email, phone in clients_data:
            c = self.client_repo.create(Client(None, name, email, phone))
            clients.append(c)

        # --- 2. Mascotas ---
        pets_data = [
            ("Luna", "Perro", "Golden Retriever", 3, clients[0]),
            ("Max", "Perro", "Pastor Alemán", 5, clients[1]),
            ("Mishi", "Gato", "Persa", 2, clients[2]),
            ("Coco", "Ave", "Loro", 10, clients[3]),
            ("Rocky", "Perro", "Bulldog", 4, clients[0]), # Ana tiene 2
            ("Simba", "Gato", "Común Europeo", 1, clients[4]),
            ("Nala", "Gato", "Siames", 3, clients[4]),
            ("Thor", "Perro", "Husky", 2, clients[5]),
            ("Lola", "Roedor", "Hamster", 1, clients[6]),
            ("Zeus", "Perro", "Doberman", 6, clients[7]),
        ]

        pets = []
        for name, species, breed, age, owner in pets_data:
            p = self.pet_repo.create(Pet(None, name, species, breed, age, owner.id))
            pets.append(p)

        # --- 3. Citas (Pasadas y Futuras) ---
        today = date.today()
        reasons = ["Vacunación", "Revisión General", "Corte de uñas", "Desparasitación", "Consulta por vómitos", "Cirugía menor"]
        
        appointments = []
        # Crear 15 citas distribuidas en +/- 15 días
        for i in range(15):
            pet = random.choice(pets)
            days_offset = random.randint(-10, 10)
            appt_date = today + timedelta(days=days_offset)
            reason = random.choice(reasons)
            status = "Completada" if days_offset < 0 else "Pendiente"
            
            appt = self.appt_repo.create(Appointment(None, pet.id, appt_date, reason, status))
            appointments.append(appt)

            # --- 4. Historial Médico (Solo para citas pasadas/completadas) ---
            if status == "Completada":
                self.mr_repo.create(MedicalRecord(
                    None, appt.id, 
                    f"Diagnóstico preliminar de {reason}", 
                    "Reposo y medicación estándar", 
                    "El paciente se portó bien."
                ))
                
                # --- 5. Facturas (Solo para citas completadas) ---
                if random.choice([True, False]): # A veces se factura
                    amount = random.randint(30, 150)
                    self.bill_repo.create(Invoice(None, pet.client_id, appt_date, float(amount), "Pagada"))

        # --- 6. Reseñas ---
        review_comments = ["Excelente servicio", "Muy amables", "Tiempos de espera largos", "Mi perro salió feliz", "Volveré seguro"]
        for client in clients[:5]: # Solo los primeros 5 dejan review
            self.review_repo.create(Review(
                None, client.id, random.randint(3, 5), random.choice(review_comments), today
            ))

        logger.info("Carga de datos masiva completada exitosamente.")