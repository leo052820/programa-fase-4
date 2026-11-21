"""
excepciones.py
Excepciones personalizadas del sistema de gestion de servicios.

Todas heredan de SoftwareFJError, asi el sistema puede capturar
cualquier error propio con un solo bloque except y, al mismo tiempo,
distinguir el tipo exacto de falla cuando lo necesite.
"""


class SoftwareFJError(ValueError):  # Excepcion base; hereda de ValueError para ser compatible con la version inicial
    """Error general del sistema; incluye un codigo para identificarlo."""

    def __init__(self, mensaje, codigo="FJ-000"):  # Recibe el mensaje y un codigo de error
        super().__init__(mensaje)  # Inicializa la clase Exception con el mensaje
        self.mensaje = mensaje  # Guarda el mensaje para mostrarlo o registrarlo
        self.codigo = codigo  # Guarda el codigo que identifica el tipo de error

    def __str__(self):  # Define como se muestra el error como texto
        return f"[{self.codigo}] {self.mensaje}"  # Formato: [codigo] mensaje


class ValidacionError(SoftwareFJError):  # Dato con formato o valor invalido
    """Se lanza cuando un dato no cumple las reglas de validacion."""

    def __init__(self, campo, mensaje):  # Recibe el campo que fallo y la razon
        super().__init__(f"Campo '{campo}': {mensaje}", "FJ-100")  # Mensaje con el nombre del campo
        self.campo = campo  # Guarda el nombre del campo invalido


class ParametroFaltanteError(SoftwareFJError):  # Falta un dato obligatorio
    """Se lanza cuando no se envia un parametro requerido."""

    def __init__(self, parametro):  # Recibe el nombre del parametro faltante
        super().__init__(f"Falta el dato obligatorio '{parametro}'", "FJ-110")  # Mensaje del error
        self.parametro = parametro  # Guarda el parametro para consultarlo despues


class ClienteError(SoftwareFJError):  # Cliente duplicado o inexistente
    """Se lanza cuando un cliente no se puede registrar o no existe."""

    def __init__(self, mensaje):  # Recibe la descripcion del problema
        super().__init__(mensaje, "FJ-200")  # Codigo de errores de clientes


class ServicioNoDisponibleError(SoftwareFJError):  # El servicio no se puede prestar
    """Se lanza cuando un servicio no existe o no tiene disponibilidad."""

    def __init__(self, mensaje):  # Recibe la descripcion del problema
        super().__init__(mensaje, "FJ-300")  # Codigo de errores de servicios


class StockInsuficienteError(ServicioNoDisponibleError):  # No hay unidades suficientes
    """Se lanza cuando se piden mas equipos de los que hay en inventario."""

    def __init__(self, equipo, disponibles, solicitados):  # Recibe equipo, disponibles y solicitados
        super().__init__(f"Stock insuficiente para '{equipo}'. "  # Construye el mensaje detallado
                         f"Disponibles: {disponibles}, Solicitados: {solicitados}.")  # Muestra disponibles vs solicitados
        self.codigo = "FJ-305"  # Codigo especifico de inventario


class CalculoInconsistenteError(SoftwareFJError):  # Un calculo dio un resultado imposible
    """Se lanza cuando un precio resulta cero, negativo o inconsistente."""

    def __init__(self, mensaje):  # Recibe la descripcion del calculo fallido
        super().__init__(mensaje, "FJ-310")  # Codigo de errores de calculo


class ReservaError(SoftwareFJError):  # Error en el ciclo de vida de una reserva
    """Se lanza cuando una reserva no existe o no se puede procesar."""

    def __init__(self, mensaje):  # Recibe la descripcion del problema
        super().__init__(mensaje, "FJ-400")  # Codigo de errores de reservas


class OperacionNoPermitidaError(ReservaError):  # Cambio de estado no permitido
    """Se lanza cuando se intenta una operacion que el estado de la reserva no permite."""

    def __init__(self, estado_actual, operacion):  # Recibe el estado actual y la operacion pedida
        super().__init__(f"No se puede {operacion} una reserva en estado {estado_actual}")  # Mensaje
        self.codigo = "FJ-410"  # Codigo especifico de operaciones no permitidas
