"""
excepciones.py
Excepciones personalizadas del sistema Software FJ.

Todas heredan de SoftwareFJError, así el sistema puede capturar
cualquier error propio con un solo bloque except y, al mismo tiempo,
distinguir el tipo exacto de falla cuando lo necesite.
"""


class SoftwareFJError(Exception):                      # Excepción base de todo el sistema
    """Error general del sistema Software FJ."""

    def __init__(self, mensaje, codigo="FJ-000"):
        """Recibe el mensaje y un código de error."""
        super().__init__(mensaje)                      # Inicializa la clase Exception con el mensaje
        self.mensaje = mensaje                         # Guarda el mensaje para mostrarlo o registrarlo
        self.codigo = codigo                           # Guarda un código que identifica el tipo de error

    def __str__(self):
        """Define cómo se muestra el error como texto."""
        return f"[{self.codigo}] {self.mensaje}"       # Formato: [código] mensaje


class ValidacionError(SoftwareFJError):                # Datos con formato o valor inválido
    """Se lanza cuando un dato no cumple las reglas de validación."""

    def __init__(self, campo, mensaje):
        """Recibe el campo que falló y la razón."""
        super().__init__(f"Campo '{campo}': {mensaje}", "FJ-100")  # Construye el mensaje con el campo
        self.campo = campo                             # Guarda el nombre del campo inválido


class ParametroFaltanteError(SoftwareFJError):         # Falta un parámetro obligatorio
    """Se lanza cuando no se envía un parámetro requerido."""

    def __init__(self, parametro):
        """Recibe el nombre del parámetro faltante."""
        super().__init__(f"Falta el parámetro obligatorio '{parametro}'", "FJ-110")
        self.parametro = parametro                     # Guarda el parámetro para consultarlo después


class ClienteInvalidoError(SoftwareFJError):           # Error al registrar o usar un cliente
    """Se lanza cuando un cliente no puede registrarse o no es válido."""

    def __init__(self, mensaje):
        """Recibe la descripción del problema."""
        super().__init__(mensaje, "FJ-200")            # Código de errores de clientes


class ServicioNoDisponibleError(SoftwareFJError):      # El servicio existe pero no se puede usar
    """Se lanza cuando se intenta reservar un servicio no disponible."""

    def __init__(self, nombre_servicio):
        """Recibe el nombre del servicio."""
        super().__init__(f"El servicio '{nombre_servicio}' no está disponible", "FJ-300")
        self.nombre_servicio = nombre_servicio         # Guarda el nombre del servicio


class StockInsuficienteError(ServicioNoDisponibleError):   # No hay unidades suficientes del equipo
    """Se lanza cuando se piden más equipos de los que hay en inventario."""

    def __init__(self, equipo, disponibles, solicitados):
        """Recibe el equipo, las unidades disponibles y las solicitadas."""
        super().__init__(equipo)                       # Inicializa como servicio no disponible
        self.mensaje = (f"Stock insuficiente de '{equipo}': "
                        f"disponibles {disponibles}, solicitados {solicitados}")   # Mensaje más detallado
        self.codigo = "FJ-305"                         # Código específico de inventario
        self.args = (self.mensaje,)                    # Actualiza el texto de la excepción


class CalculoInconsistenteError(SoftwareFJError):      # Un cálculo dio un resultado imposible
    """Se lanza cuando un costo resulta negativo o inconsistente."""

    def __init__(self, mensaje):
        """Recibe la descripción del cálculo fallido."""
        super().__init__(mensaje, "FJ-310")            # Código de errores de cálculo


class ReservaError(SoftwareFJError):                   # Error en el ciclo de vida de una reserva
    """Se lanza cuando una reserva no se puede crear, confirmar o procesar."""

    def __init__(self, mensaje):
        """Recibe la descripción del problema."""
        super().__init__(mensaje, "FJ-400")            # Código de errores de reservas


class OperacionNoPermitidaError(ReservaError):         # Cambio de estado no permitido
    """Se lanza cuando se intenta una transición de estado inválida."""

    def __init__(self, estado_actual, operacion):
        """Recibe el estado actual y la operación pedida."""
        super().__init__(f"No se puede '{operacion}' una reserva en estado {estado_actual}")
        self.codigo = "FJ-410"                         # Sobrescribe el código con uno más específico
