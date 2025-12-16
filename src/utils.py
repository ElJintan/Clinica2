import logging
import re
from datetime import datetime

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)
logger = logging.getLogger("VeterinariaApp")

class Validators:
    """Clase utilitaria estática para validaciones comunes."""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        if not email: return False
        regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.match(regex, email) is not None

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Valida que el teléfono tenga entre 7 y 15 dígitos numéricos."""
        if not phone: return False
        # Permite opcionalmente un + al inicio, seguido de 7 a 15 digitos
        regex = r'^\+?\d{7,15}$' 
        return re.match(regex, phone) is not None

    @staticmethod
    def is_not_empty(text: str) -> bool:
        """Valida que un string no sea None y no esté vacío o solo contenga espacios."""
        return bool(text and text.strip())

    @staticmethod
    def is_positive_number(number: float) -> bool:
        """Valida que un número sea mayor que 0."""
        return number is not None and number > 0

    @staticmethod
    def is_non_negative(number: int) -> bool:
        """Valida que un número sea mayor o igual a 0."""
        return number is not None and number >= 0

    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        try:
            datetime.strptime(str(date_str), '%Y-%m-%d')
            return True
        except ValueError:
            return False