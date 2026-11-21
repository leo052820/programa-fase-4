"""
reserva.py
Clase Reserva: integra cliente, servicio, duración y estado.
Implementa confirmar(), cancelar() y procesar() con manejo de excepciones.
"""

from enum import Enum                                  # Para definir los estados posibles
from .entidad import EntidadBase                       # Clase abstracta base
from .cliente import Cliente                           # Para validar el tipo de cliente
from .servicios import Servicio, IVA                   # Para validar el tipo de servicio
from .excepciones import (ReservaError, OperacionNoPermitidaError,
                          ServicioNoDisponibleError, SoftwareFJError)
from .registro import obtener_logger                   # Registro de eventos en el archivo de logs

log = obtener_logger()                                 # Logger compartido del sistema


class EstadoReserva(Enum):
    """Estados del ciclo de vida de una reserva."""
    PENDIENTE = "PENDIENTE"                            # Creada, aún no confirmada
    CONFIRMADA = "CONFIRMADA"                          # Confirmada por el cliente
    PROCESADA = "PROCESADA"                            # Cobrada y finalizada
    CANCELADA = "CANCELADA"                            # Anulada


class Reserva(EntidadBase):                            # Reserva hereda ID y fecha de EntidadBase
    """Reserva de un servicio por parte de un cliente."""

    def __init__(self, cliente, servicio, horas):
        """Recibe cliente, servicio y duración."""
        if not isinstance(cliente, Cliente):           # Debe recibir un objeto Cliente
            raise ReservaError("La reserva necesita un cliente válido")
        if not isinstance(servicio, Servicio):         # Debe recibir un objeto Servicio
            raise ReservaError("La reserva necesita un servicio válido")
        if not servicio.disponible:                    # No se reservan servicios deshabilitados
            raise ServicioNoDisponibleError(servicio.nombre)
        servicio.validar_parametros(horas)             # Valida la duración según el tipo de servicio
        self._cliente = cliente                        # Cliente que hace la reserva
        self._servicio = servicio                      # Servicio reservado
        self._horas = horas                            # Duración solicitada
        self._estado = EstadoReserva.PENDIENTE         # Toda reserva inicia pendiente
        self._total = None                             # El total se calcula al procesar
        super().__init__("RES")                        # Solo si todo es válido se asigna el ID

    @property
    def estado(self):
        """Lectura del estado."""
        return self._estado

    @property
    def cliente(self):
        """Cliente que hizo la reserva."""
        return self._cliente

    @property
    def servicio(self):
        """Servicio reservado."""
        return self._servicio

    @property
    def total(self):
        """Lectura del total cobrado."""
        return self._total

    def _cambiar_estado(self, permitidos, nuevo, operacion):
        """Controla las transiciones de estado."""
        if self._estado not in permitidos:             # Si el estado actual no permite la operación...
            raise OperacionNoPermitidaError(self._estado.value, operacion)   # ...lanza un error
        self._estado = nuevo                           # Cambia al nuevo estado

    def confirmar(self):
        """PENDIENTE -> CONFIRMADA."""
        self._cambiar_estado({EstadoReserva.PENDIENTE}, EstadoReserva.CONFIRMADA, "confirmar")
        log.info("Reserva %s confirmada", self.id)     # Registra el evento

    def cancelar(self):
        """PENDIENTE o CONFIRMADA -> CANCELADA."""
        self._cambiar_estado({EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA},
                             EstadoReserva.CANCELADA, "cancelar")
        log.info("Reserva %s cancelada", self.id)      # Registra el evento

    def procesar(self, descuento=None):                # CONFIRMADA -> PROCESADA (calcula el cobro)
        """Calcula el total y finaliza la reserva usando try/except/else/finally."""
        try:                                           # Bloque que puede fallar
            if self._estado is not EstadoReserva.CONFIRMADA:   # Solo se procesa lo confirmado
                raise OperacionNoPermitidaError(self._estado.value, "procesar")
            total = self._servicio.calcular_costo(self._horas, impuesto=IVA, descuento=descuento)
        except OperacionNoPermitidaError:              # Error de estado: se relanza igual
            log.warning("Intento de procesar %s en estado %s", self.id, self._estado.value)
            raise                                      # Lo maneja quien llamó a procesar()
        except SoftwareFJError as error:               # Error de cálculo o validación
            log.error("Fallo al calcular el costo de %s: %s", self.id, error)
            raise ReservaError(f"No se pudo procesar la reserva {self.id}") from error   # Encadenamiento
        else:                                          # Se ejecuta solo si no hubo excepción
            self._total = total                        # Guarda el total calculado
            self._estado = EstadoReserva.PROCESADA     # Marca la reserva como procesada
            log.info("Reserva %s procesada. Total: $%s", self.id, f"{total:,.2f}")
            return total                               # Devuelve el total cobrado
        finally:                                       # Se ejecuta siempre, con o sin error
            log.info("Fin del intento de procesamiento de %s (estado: %s)", self.id, self._estado.value)

    def validar(self):
        """Revalida cliente y servicio de la reserva."""
        return self._cliente.validar() and self._servicio.validar()

    def describir(self):
        """Descripción de la reserva."""
        total = f"${self._total:,.2f}" if self._total is not None else "por calcular"
        return (f"{self.id} | {self._cliente.nombre} -> {self._servicio.nombre} | "
                f"{self._horas:g} h | {self._estado.value} | Total: {total}")
