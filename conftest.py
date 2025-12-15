import sys
import os

# Esto añade la carpeta raíz del proyecto al "camino" de Python.
# Sin esto, los tests no sabrían dónde encontrar la carpeta 'src'.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))