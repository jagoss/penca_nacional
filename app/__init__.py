"""
App de Penca Electoral Uruguaya.

Este paquete contiene los módulos necesarios para la aplicación de
predicciones electorales para las elecciones municipales de Uruguay 2025.

Módulos:
    - candidatos: Datos de candidatos a intendencias
    - candidatos_alcalde: Datos de candidatos a alcaldías en Montevideo
    - menu_handler: Manejo de menús y funciones principales
    - visualizador_mapa: Visualización geográfica de resultados y predicciones
"""

import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Definición de rutas de archivos
FILES_DIR = os.path.join(APP_DIR, "files")
PREDICCIONES_FILE = os.path.join(FILES_DIR, "predicciones.json")
RESULTADOS_FILE = os.path.join(FILES_DIR, "resultados.json")
GEOJSON_FILE = os.path.join(APP_DIR, "files", "departamentos_uy.geojson")

# Asegurar que la carpeta 'files' existe
os.makedirs(FILES_DIR, exist_ok=True)

# Versión del paquete
__version__ = "0.1.0"

# Variables útiles disponibles al nivel del paquete
DEPARTAMENTOS = [
    "Artigas",
    "Canelones",
    "Cerro Largo",
    "Colonia",
    "Durazno",
    "Flores",
    "Florida",
    "Lavalleja",
    "Maldonado",
    "Montevideo",
    "Paysandú",
    "Río Negro",
    "Rivera",
    "Rocha",
    "Salto",
    "San José",
    "Soriano",
    "Tacuarembó",
    "Treinta y Tres",
]


# Función útil para manejar archivos JSON
def ensure_files_exist():
    """Asegura que los archivos JSON necesarios existan, creándolos vacíos si no existen."""
    if not os.path.exists(PREDICCIONES_FILE):
        with open(PREDICCIONES_FILE, "w", encoding="utf-8") as f:
            f.write("{}")

    if not os.path.exists(RESULTADOS_FILE):
        with open(RESULTADOS_FILE, "w", encoding="utf-8") as f:
            f.write("{}")


# Crear los archivos vacíos si no existen
ensure_files_exist()

# Importar funciones clave al final para evitar importaciones circulares
# Nota: esto se hace después de definir las constantes para evitar problemas
from app.menu_handler import (cargar_resultados, hacer_prediccion, ver_mapa,
                              ver_puntajes)
