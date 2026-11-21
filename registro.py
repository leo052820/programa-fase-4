"""
registro.py
Configuracion del archivo de logs del sistema.

El sistema no usa base de datos: los eventos y errores se guardan en
el archivo sistema.log (junto a los demas archivos) para revisarlos despues.
"""

import logging  # Modulo estandar de Python para registrar eventos
from pathlib import Path  # Manejo de rutas de archivos y carpetas

ARCHIVO_LOG = Path(__file__).resolve().parent / "sistema.log"  # Archivo de logs junto a este archivo


def obtener_logger(nombre="sistema_servicios"):  # Devuelve el logger listo para usar
    """Crea (una sola vez) y devuelve el logger del sistema."""
    logger = logging.getLogger(nombre)  # Obtiene o crea el logger con ese nombre
    if logger.handlers:  # Si ya fue configurado antes...
        return logger  # ...lo devuelve sin duplicar manejadores
    logger.setLevel(logging.INFO)  # Registra eventos de nivel INFO o superior
    try:  # Intenta crear o abrir el archivo de logs
        manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")  # Escribe en el archivo
    except OSError:  # Si no hay permisos de escritura en disco...
        manejador = logging.StreamHandler()  # ...registra en consola para no detener el sistema
    formato = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s",  # Fecha | nivel | mensaje
                                datefmt="%Y-%m-%d %H:%M:%S")  # Formato de la fecha
    manejador.setFormatter(formato)  # Aplica el formato al manejador
    logger.addHandler(manejador)  # Conecta el manejador al logger
    return logger  # Devuelve el logger configurado
