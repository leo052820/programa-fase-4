"""
entidad.py
Clase abstracta que representa cualquier entidad general del sistema.
Cliente, Servicio y Reserva heredan de ella.
"""

from abc import ABC, abstractmethod                    # Herramientas para definir clases abstractas
from datetime import datetime                          # Para registrar la fecha de creación


class EntidadBase(ABC):                                # Clase abstracta: no se puede instanciar directamente
    """Entidad general: tiene un identificador único y una fecha de creación."""

    _contadores = {}                                   # Un contador por prefijo: {"CLI": 2, "SRV": 3, ...}

    def __init__(self, prefijo):
        """Recibe un prefijo para el ID (CLI, SRV, RES)."""
        numero = EntidadBase._contadores.get(prefijo, 0) + 1   # Siguiente número para ese prefijo
        EntidadBase._contadores[prefijo] = numero      # Actualiza el contador
        self._id = f"{prefijo}-{numero:03d}"           # Construye un ID como CLI-001
        self._fecha_creacion = datetime.now()          # Guarda el momento en que se creó la entidad

    @property                                          # Permite leer el ID como atributo
    def id(self):
        """Identificador único de la entidad (solo lectura)."""
        return self._id                                # El ID es de solo lectura (encapsulación)

    @property                                          # Permite leer la fecha de creación
    def fecha_creacion(self):
        """Fecha y hora en que se creó la entidad (solo lectura)."""
        return self._fecha_creacion                    # También es de solo lectura

    @abstractmethod                                    # Las clases hijas deben implementarlo
    def describir(self):
        """Devuelve una descripción en texto de la entidad."""

    @abstractmethod                                    # Las clases hijas deben implementarlo
    def validar(self):
        """Verifica que la entidad sea consistente; lanza una excepción si no lo es."""

    def __str__(self):
        """Representación en texto común a todas las entidades."""
        return self.describir()                        # Usa el método polimórfico describir()
