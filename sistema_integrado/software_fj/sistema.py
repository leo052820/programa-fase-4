"""
sistema.py
Clase SistemaGestion: administra clientes, servicios, reservas e
inventario de equipos en estructuras internas (sin base de datos).
Cada operación captura sus errores, los registra en el log y permite
que el sistema siga activo.
"""

from .cliente import Cliente                           # Clase de clientes
from .servicios import ReservaSala, AlquilerEquipo, Asesoria   # Servicios especializados
from .reserva import Reserva                           # Clase de reservas
from .excepciones import (SoftwareFJError, ClienteInvalidoError, ReservaError,
                          StockInsuficienteError)      # Errores que maneja el sistema
from .registro import obtener_logger                   # Registro de eventos y errores

log = obtener_logger()                                 # Logger compartido del sistema

TIPOS_SERVICIO = {                                     # Relaciona un nombre de tipo con su clase
    "sala": ReservaSala,
    "equipo": AlquilerEquipo,
    "asesoria": Asesoria,
}

INVENTARIO_INICIAL = {                                 # Unidades disponibles de cada equipo
    "Laptop": 10,
    "Tablet": 8,
    "Camara": 5,
    "Kit VR": 3,
}


class SistemaGestion:
    """Punto central de la aplicación Software FJ."""

    def __init__(self):
        """Crea el sistema con sus listas internas vacías y el inventario inicial."""
        self.clientes = []                             # Lista interna de clientes
        self.servicios = []                            # Lista interna de servicios
        self.reservas = []                             # Lista interna de reservas
        self.inventario = dict(INVENTARIO_INICIAL)     # Copia del inventario de equipos
        self.errores = 0                               # Contador de operaciones fallidas
        log.info("=== Sistema Software FJ iniciado ===")

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------
    def _fallo(self, operacion, error):
        """Cuenta, registra y muestra un error sin detener el sistema."""
        self.errores += 1                              # Cuenta el error
        log.error("%s -> %s%s", operacion, error, self._texto_causa(error))   # Lo guarda en el log
        print(f"   ✗ ERROR: {error}{self._texto_causa(error)}")              # Lo muestra al usuario

    @staticmethod
    def _texto_causa(error):
        """Devuelve el texto de la excepción original encadenada, si existe."""
        causa = error.__cause__                        # Excepción original (raise ... from ...)
        if causa is None:                              # Sin encadenamiento
            return ""
        if isinstance(causa, SoftwareFJError):         # Causa propia: se muestra con su código
            return f" | causa: {causa}"
        return f" | causa: {type(causa).__name__}: {causa}"   # Causa de Python: se muestra su tipo

    @staticmethod
    def _exito(mensaje, entidad):
        """Registra y muestra una operación exitosa."""
        log.info("%s: %s", mensaje, entidad.describir())     # Lo guarda en el log
        print(f"   ✓ {mensaje}: {entidad.describir()}")      # Lo muestra al usuario

    # ------------------------------------------------------------------
    # Clientes
    # ------------------------------------------------------------------
    def registrar_cliente(self, **datos):
        """Registra un cliente; devuelve el Cliente o None si hubo un error."""
        cliente = None                                 # Resultado por defecto: sin cliente
        try:
            if any(c.documento == str(datos.get("documento")) for c in self.clientes):   # Evita duplicados
                raise ClienteInvalidoError(f"Ya existe un cliente con documento {datos.get('documento')}")
            cliente = Cliente(**datos)                 # Puede lanzar ValidacionError o ParametroFaltanteError
        except TypeError as error:                     # Parámetros inesperados (error de Python)
            nuevo = ClienteInvalidoError("Datos incompletos o incorrectos")
            nuevo.__cause__ = error                    # Encadena el error original
            self._fallo("Registrar cliente", nuevo)
        except SoftwareFJError as error:               # Errores propios del sistema
            self._fallo("Registrar cliente", error)
        else:                                          # Solo si no hubo error
            self.clientes.append(cliente)              # Agrega el cliente a la lista
            self._exito("Cliente registrado", cliente)
        return cliente                                 # Cliente creado o None

    def buscar_cliente(self, documento):
        """Busca un cliente por documento; devuelve el Cliente o None."""
        for cliente in self.clientes:                  # Recorre la lista de clientes
            if cliente.documento == str(documento).strip():   # Compara el documento
                return cliente                         # Lo encontró
        self._fallo("Buscar cliente", ClienteInvalidoError(f"No existe un cliente con documento {documento}"))
        return None                                    # No lo encontró

    # ------------------------------------------------------------------
    # Servicios
    # ------------------------------------------------------------------
    def crear_servicio(self, tipo, **datos):
        """Crea un servicio ("sala", "equipo" o "asesoria"); devuelve el servicio o None."""
        servicio = None                                # Resultado por defecto: sin servicio
        try:
            clase = TIPOS_SERVICIO[tipo]               # KeyError si el tipo no existe
            servicio = clase(**datos)                  # Crea el servicio especializado
        except KeyError as error:                      # Tipo de servicio desconocido
            nuevo = SoftwareFJError(f"Tipo de servicio desconocido: '{tipo}'", "FJ-320")
            nuevo.__cause__ = error                    # Encadena el error original
            self._fallo("Crear servicio", nuevo)
        except TypeError as error:                     # Faltan o sobran parámetros
            nuevo = SoftwareFJError(f"Parámetros incorrectos para '{tipo}'", "FJ-330")
            nuevo.__cause__ = error                    # Encadena el error original
            self._fallo("Crear servicio", nuevo)
        except SoftwareFJError as error:               # Validaciones propias del servicio
            self._fallo("Crear servicio", error)
        else:                                          # Solo si no hubo error
            self.servicios.append(servicio)            # Agrega el servicio a la lista
            self._exito("Servicio creado", servicio)
        return servicio                                # Servicio creado o None

    # ------------------------------------------------------------------
    # Inventario de equipos
    # ------------------------------------------------------------------
    def _verificar_stock(self, servicio):
        """Comprueba que haya unidades suficientes para un alquiler de equipos."""
        if not isinstance(servicio, AlquilerEquipo):   # Solo los equipos manejan stock
            return
        disponibles = self.inventario.get(servicio.nombre, 0)   # Unidades disponibles del equipo
        if servicio.cantidad > disponibles:            # No alcanza el stock
            raise StockInsuficienteError(servicio.nombre, disponibles, servicio.cantidad)

    def _descontar_stock(self, servicio):
        """Descuenta del inventario las unidades de un alquiler de equipos."""
        if isinstance(servicio, AlquilerEquipo) and servicio.nombre in self.inventario:
            self.inventario[servicio.nombre] -= servicio.cantidad   # Descuenta las unidades

    def _devolver_stock(self, servicio):
        """Repone en el inventario las unidades de un alquiler cancelado."""
        if isinstance(servicio, AlquilerEquipo) and servicio.nombre in self.inventario:
            self.inventario[servicio.nombre] += servicio.cantidad   # Devuelve las unidades
            log.info("Stock repuesto: %s x%s", servicio.nombre, servicio.cantidad)

    def texto_inventario(self):
        """Devuelve el inventario en una línea de texto."""
        return " | ".join(f"{equipo}: {stock}" for equipo, stock in self.inventario.items())

    # ------------------------------------------------------------------
    # Reservas
    # ------------------------------------------------------------------
    def crear_reserva(self, cliente, servicio, horas):
        """Crea una reserva pendiente y aparta los equipos; devuelve la Reserva o None."""
        reserva = None                                 # Resultado por defecto: sin reserva
        try:
            self._verificar_stock(servicio)            # Puede lanzar StockInsuficienteError
            reserva = Reserva(cliente, servicio, horas)    # Valida cliente, servicio y horas
        except SoftwareFJError as error:
            self._fallo("Crear reserva", error)
        else:                                          # Solo si no hubo error
            self._descontar_stock(servicio)            # Aparta los equipos del inventario
            self.reservas.append(reserva)              # Agrega la reserva a la lista
            self._exito("Reserva creada", reserva)
        return reserva                                 # Reserva creada o None

    def buscar_reserva(self, identificador):
        """Busca una reserva por ID ("RES-001" o "1"); devuelve la Reserva o None."""
        texto = str(identificador).strip().upper()     # Normaliza lo que escribió el usuario
        if texto.isdigit():                            # Si solo escribió el número...
            texto = f"RES-{int(texto):03d}"            # ...lo convierte al formato RES-001
        for reserva in self.reservas:                  # Recorre la lista de reservas
            if reserva.id == texto:
                return reserva                         # La encontró
        self._fallo("Buscar reserva", ReservaError(f"No existe la reserva {identificador}"))
        return None                                    # No la encontró

    def confirmar_y_procesar(self, reserva, descuento=None):
        """Confirma y cobra una reserva; devuelve el total o None si falla."""
        if reserva is None:                            # Si la reserva no se pudo crear antes...
            self._fallo("Procesar reserva", ReservaError("No hay reserva para procesar"))
            return None                                # ...no intenta procesarla
        total = None                                   # Resultado por defecto: sin cobro
        try:
            reserva.confirmar()                        # Puede lanzar OperacionNoPermitidaError
            total = reserva.procesar(descuento)        # Puede lanzar ReservaError encadenado
        except SoftwareFJError as error:
            self._fallo(f"Procesar {reserva.id}", error)
        else:                                          # Solo si no hubo error
            self._exito("Reserva procesada", reserva)
        finally:                                       # Siempre: deja constancia del estado final
            log.info("Estado final de %s: %s", reserva.id, reserva.estado.value)
        return total                                   # Total cobrado o None

    def cancelar_reserva(self, reserva):
        """Cancela una reserva usando try/except/finally; devuelve True si se canceló."""
        cancelada = False                              # Resultado por defecto
        try:
            reserva.cancelar()                         # Puede lanzar OperacionNoPermitidaError
            self._devolver_stock(reserva.servicio)     # Si era un alquiler, repone los equipos
            cancelada = True                           # Solo llega aquí si no hubo error
            self._exito("Reserva cancelada", reserva)
        except SoftwareFJError as error:
            self._fallo(f"Cancelar {reserva.id}", error)
        finally:                                       # Siempre: deja constancia del intento
            log.info("Intento de cancelación de %s: %s", reserva.id, "exitoso" if cancelada else "fallido")
        return cancelada

    def cotizar_servicio(self, servicio, duracion):
        """Cotiza un servicio; devuelve el valor o None si el cálculo no es válido."""
        valor = None                                   # Resultado por defecto: sin cotización
        try:
            valor = servicio.cotizar(duracion)         # Puede lanzar ValidacionError o CalculoInconsistenteError
        except SoftwareFJError as error:
            self._fallo(f"Cotizar '{servicio.nombre}'", error)
        else:                                          # Solo si no hubo error
            log.info("Cotización de %s (%s): $%s", servicio.nombre, duracion, f"{valor:,.2f}")
        return valor                                   # Valor cotizado o None

    # ------------------------------------------------------------------
    # Reportes
    # ------------------------------------------------------------------
    def resumen(self):
        """Devuelve un texto con el estado general del sistema."""
        procesadas = [r for r in self.reservas if r.total is not None]   # Reservas cobradas
        ingresos = sum(r.total for r in procesadas)    # Suma de lo cobrado
        return (f"Clientes: {len(self.clientes)} | Servicios: {len(self.servicios)} | "
                f"Reservas: {len(self.reservas)} | Procesadas: {len(procesadas)} | "
                f"Ingresos: ${ingresos:,.2f} | Errores controlados: {self.errores}")
