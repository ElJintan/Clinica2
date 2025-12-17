import sqlite3
import os
from src.utils import logger

class DatabaseManager:
    """Manejo de conexión a SQLite."""
    
    def __init__(self, db_name="veterinaria_final.db"):
        self._conn_cache = None # Variable para guardar la conexión en memoria
        
        # Detectar si es una base de datos en memoria (para tests)
        if db_name == ":memory:":
            self.db_name = ":memory:"
            self.is_memory = True
        else:
            # Construimos la ruta absoluta para bases de datos en archivo
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_name = os.path.join(base_dir, db_name)
            self.is_memory = False

    def get_connection(self):
        # check_same_thread=False es necesario para Streamlit y tests
        
        # LÓGICA ESPECIAL PARA MEMORIA (TESTS)
        if self.is_memory:
            # Si ya tenemos una conexión abierta, la reutilizamos (Singleton)
            # Esto evita que la base de datos se borre entre initialize_db y el test
            if self._conn_cache is None:
                self._conn_cache = sqlite3.connect(self.db_name, check_same_thread=False)
            return self._conn_cache
            
        # LÓGICA NORMAL (ARCHIVO)
        # Siempre devolvemos una conexión nueva
        return sqlite3.connect(self.db_name, check_same_thread=False)

    def initialize_db(self):
        """Crea las tablas si no existen."""
        try:
            # Usamos get_connection. Si es memoria, usará la cacheada.
            # Nota: El 'with' en sqlite3 hace commit/rollback, pero NO cierra la conexión automáticamente,
            # lo cual es perfecto para nuestro caso de memoria.
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # --- Tabla Clientes ---
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        phone TEXT NOT NULL
                    )
                ''')
                
                # --- Tabla Mascotas ---
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        species TEXT NOT NULL,
                        breed TEXT NOT NULL,
                        age INTEGER,
                        client_id INTEGER,
                        FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
                    )
                ''')
                
                # --- Tabla Citas ---
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS appointments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pet_id INTEGER,
                        date DATE,
                        reason TEXT,
                        status TEXT,
                        FOREIGN KEY(pet_id) REFERENCES pets(id) ON DELETE CASCADE
                    )
                ''')
                
                # --- Tabla Historial Médico ---
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS medical_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        appointment_id INTEGER,
                        diagnosis TEXT NOT NULL,
                        treatment TEXT NOT NULL,
                        notes TEXT,
                        FOREIGN KEY(appointment_id) REFERENCES appointments(id) ON DELETE CASCADE
                    )
                ''')

                # --- Tabla Facturas ---
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS invoices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id INTEGER,
                        date DATE NOT NULL,
                        total_amount REAL NOT NULL,
                        status TEXT NOT NULL,
                        FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
                    )
                ''')
                
                # --- Tabla Reseñas ---
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reviews (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id INTEGER,
                        rating INTEGER NOT NULL,
                        comment TEXT,
                        review_date DATE NOT NULL,
                        FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
                    )
                ''')

                # --- Tabla Usuarios (LOGIN) ---
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT DEFAULT 'admin'
                    )
                """)

                logger.info(f"Base de datos inicializada en: {self.db_name}")
                
        except Exception as e:
            logger.error(f"Error inicializando DB: {e}")
            raise