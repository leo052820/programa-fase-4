"""
registro.py
Configuración del archivo de logs del sistema.

El sistema no usa base de datos: los eventos y errores se guardan en
el archivo logs/software_fj.log para poder revisarlos después.
"""

import logging                                         # Módulo estándar de Python para registrar eventos
from pathlib import Path                               # Manejo de rutas de archivos y carpetas

CARPETA_LOGS = Path(__file__).resolve().parent.parent / "logs"   # Carpeta logs/ en la raíz del proyecto
ARCHIVO_LOG = CARPETA_LOGS / "software_fj.log"                   # Ruta completa del archivo de logs


def obtener_logger(nombre="software_fj"):              # Devuelve un logger listo para usar
    """Crea (una sola vez) y devuelve el logger del sistema."""
    logger = logging.getLogger(nombre)                 # Obtiene o crea el logger con ese nombre
    if logger.handlers:                                # Si ya fue configurado antes...
        return logger                                  # ...lo devuelve sin duplicar manejadores
    logger.setLevel(logging.INFO)                      # Registra eventos de nivel INFO o superior
    try:                                               # Intenta crear la carpeta y el archivo de logs
        CARPETA_LOGS.mkdir(exist_ok=True)              # Crea logs/ si no existe
        manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")  # Escribe en el archivo
    except OSError:                                    # Si no hay permisos de escritura en disco...
        manejador = logging.StreamHandler()            # ...registra en la consola para no detener el sistema
    formato = logging.Formatter(                       # Formato de cada línea del log
        "%(asctime)s | %(levelname)-8s | %(message)s",  # Fecha y hora | nivel | mensaje
        datefmt="%Y-%m-%d %H:%M:%S",                   # Formato de la fecha
    )
    manejador.setFormatter(formato)                    # Aplica el formato al manejador
    logger.addHandler(manejador)                       # Conecta el manejador al logger
    return logger                                      # Devuelve el logger configurado
