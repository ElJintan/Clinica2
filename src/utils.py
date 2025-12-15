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
        regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.match(regex, email) is not None

    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        try:
            datetime.strptime(str(date_str), '%Y-%m-%d')
            return True
        except ValueError:
            return False