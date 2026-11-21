"""
gestor.py
Logica de negocio: clientes, inventario y reservas en memoria (sin base de datos).

Version inicial: Jose Leonardo Lopez Rangel.
Complemento: Jimena Jacome Contreras (excepciones personalizadas, registro en
sistema.log, confirmacion y procesamiento de reservas, try/except/else/finally
y encadenamiento de excepciones).
"""

from modelo import Cliente, Servicio, Reserva, AlquilerEquipo  # Importa las clases del modelo de dominio
from excepciones import (SoftwareFJError, ClienteError, ReservaError,
                         StockInsuficienteError, ServicioNoDisponibleError)  # Complemento: excepciones del sistema
from registro import obtener_logger  # Complemento: logger que escribe en sistema.log

log = obtener_logger()  # Complemento: logger compartido por todo el gestor


class GestorEmpresa:  # Clase encargada de gestionar clientes, inventario y reservas
    """Administra clientes, inventario de equipos y reservas."""

    def __init__(self):  # Constructor que inicializa las estructuras de datos en memoria
        self.clientes = {}  # Diccionario para almacenar clientes usando el documento como clave
        self.reservas = []  # Lista para guardar el historial de reservas creadas
        self.contador_reservas = 1  # Secuencia numerica para asignar IDs unicos a cada reserva
        self.errores_controlados = 0  # Complemento: cuenta los errores que el sistema manejo sin detenerse
        self.inventario_equipos = {  # Diccionario con el stock inicial disponible por tipo de equipo
            "Laptop": 10,  # 10 laptops disponibles inicialmente
            "Tablet": 8,  # 8 tablets disponibles inicialmente
            "Camara": 5,  # 5 camaras disponibles inicialmente
            "Kit VR": 3  # 3 kits de realidad virtual disponibles inicialmente
        }
        log.info("Sistema iniciado")  # Complemento: registra el arranque en el archivo de logs

    def registrar_error(self, operacion, error):  # Complemento: centraliza el registro de errores
        """Cuenta el error y lo escribe en el log, incluyendo su causa si fue encadenado."""
        self.errores_controlados += 1  # Suma un error controlado
        error.registrado = True  # Marca el error para no registrarlo dos veces
        causa = f" | Causa: {error.__cause__}" if error.__cause__ else ""  # Causa original (encadenamiento)
        log.error("%s fallo: %s%s", operacion, error, causa)  # Escribe el error en el log

    def registrar_cliente(self, documento: str, nombre: str, correo: str) -> Cliente:  # Registra un nuevo cliente
        """Crea y guarda un cliente; lanza ClienteError si ya existe."""
        try:  # Complemento: intenta validar y registrar
            if documento in self.clientes:  # Comprueba si ya existe un cliente con ese documento
                raise ClienteError(f"Ya existe un cliente registrado con el documento {documento}.")  # Lanza error si esta duplicado
            cliente = Cliente(documento, nombre, correo)  # Crea la instancia de Cliente
        except SoftwareFJError as error:  # Complemento: errores de validacion o duplicado
            self.registrar_error("Registro de cliente", error)  # Lo deja en el log
            raise  # Lo propaga para que la interfaz lo muestre
        else:  # Complemento: solo se ejecuta si no hubo errores
            self.clientes[cliente.documento] = cliente  # Almacena el cliente en el diccionario usando su documento
            log.info("Cliente registrado: %s", cliente)  # Registra el exito
            return cliente  # Retorna el cliente recien registrado

    def buscar_cliente(self, documento: str) -> Cliente:  # Busca un cliente por su numero de documento
        """Devuelve el cliente o lanza ClienteError si no existe."""
        cliente = self.clientes.get(documento)  # Obtiene el cliente si existe o None si no se encuentra
        if not cliente:  # Si no se encontro el cliente
            raise ClienteError(f"No se encontro ningun cliente con documento {documento}.")  # Lanza error informativo
        return cliente  # Retorna el objeto Cliente encontrado

    def buscar_reserva(self, id_reserva: int) -> Reserva:  # Complemento: busca una reserva por su ID
        """Devuelve la reserva o lanza ReservaError si no existe."""
        for reserva in self.reservas:  # Recorre todas las reservas registradas
            if reserva.id_reserva == id_reserva:  # Busca coincidencia con el ID solicitado
                return reserva  # Retorna la reserva encontrada
        raise ReservaError(f"No existe una reserva con el ID #{id_reserva}.")  # Lanza error si no se hallo el ID

    def crear_reserva(self, documento_cliente: str, servicio: Servicio) -> Reserva:  # Crea y registra una reserva
        """Crea una reserva ACTIVA y descuenta stock si es alquiler de equipo."""
        try:  # Complemento: intenta crear la reserva
            cliente = self.buscar_cliente(documento_cliente)  # Valida que el cliente exista y obtiene su objeto

            if isinstance(servicio, AlquilerEquipo):  # Verifica si el servicio solicitado es alquiler de equipo
                if servicio.nombre_equipo not in self.inventario_equipos:  # Complemento: el equipo debe existir
                    raise ServicioNoDisponibleError(f"El equipo '{servicio.nombre_equipo}' no existe en el catalogo.")
                disponibles = self.inventario_equipos.get(servicio.nombre_equipo, 0)  # Consulta unidades disponibles del equipo
                if servicio.cantidad > disponibles:  # Revisa si hay suficiente stock para cubrir la solicitud
                    raise StockInsuficienteError(servicio.nombre_equipo, disponibles, servicio.cantidad)  # Sin stock

            nueva_reserva = Reserva(self.contador_reservas, cliente, servicio)  # Instancia la nueva reserva con su ID
        except SoftwareFJError as error:  # Complemento: captura cualquier error propio del sistema
            self.registrar_error("Creacion de reserva", error)  # Lo deja en el log
            raise  # Lo propaga a quien llamo
        else:  # Complemento: solo si todo salio bien se modifican los datos
            if isinstance(servicio, AlquilerEquipo):  # Si es alquiler de equipo
                self.inventario_equipos[servicio.nombre_equipo] -= servicio.cantidad  # Descuenta las unidades alquiladas del inventario
            self.reservas.append(nueva_reserva)  # Agrega la reserva a la lista general de reservas
            self.contador_reservas += 1  # Incrementa el contador para la siguiente reserva
            log.info("Reserva creada: %s", nueva_reserva)  # Registra el exito
            return nueva_reserva  # Retorna la reserva creada

    def confirmar_reserva(self, id_reserva: int) -> Reserva:  # Complemento: confirma una reserva activa
        """Pasa la reserva de ACTIVA a CONFIRMADA."""
        try:  # Intenta confirmar
            reserva = self.buscar_reserva(id_reserva)  # Busca la reserva
            reserva.confirmar()  # Cambia su estado (puede lanzar OperacionNoPermitidaError)
        except SoftwareFJError as error:  # Reserva inexistente o estado no valido
            self.registrar_error("Confirmacion de reserva", error)  # Lo deja en el log
            raise  # Lo propaga
        log.info("Reserva #%s confirmada", id_reserva)  # Registra el exito
        return reserva  # Retorna la reserva confirmada

    def procesar_reserva(self, id_reserva: int, descuento=None) -> float:  # Complemento: cobra una reserva confirmada
        """Calcula el valor final con IVA (y descuento opcional) y marca la reserva como PROCESADA."""
        try:  # Intenta procesar
            reserva = self.buscar_reserva(id_reserva)  # Busca la reserva
            total = reserva.procesar(descuento)  # Puede lanzar un ReservaError encadenado a la causa original
        except SoftwareFJError as error:  # Captura el error (y conserva su causa en __cause__)
            self.registrar_error("Procesamiento de reserva", error)  # Registra error y causa
            raise  # Lo propaga
        else:  # Solo si el cobro fue exitoso
            log.info("Reserva #%s procesada. Cobrado: $%s", id_reserva, f"{total:,.0f}")  # Registra el cobro
            return total  # Retorna el valor cobrado

    def cancelar_reserva(self, id_reserva: int) -> Reserva:  # Cancela una reserva existente por su ID
        """Cancela la reserva y devuelve los equipos al inventario si aplica."""
        reserva = None  # Complemento: se inicializa para usarla en el bloque finally
        try:  # Complemento: intenta cancelar
            reserva = self.buscar_reserva(id_reserva)  # Busca coincidencia con el ID solicitado
            reserva.cancelar()  # Cambia el estado de la reserva a CANCELADA
            if isinstance(reserva.servicio, AlquilerEquipo):  # Si la reserva era de alquiler de equipo
                equipo = reserva.servicio.nombre_equipo  # Obtiene el nombre del equipo alquilado
                self.inventario_equipos[equipo] += reserva.servicio.cantidad  # Devuelve las unidades al inventario disponible
            log.info("Reserva #%s cancelada", id_reserva)  # Complemento: registra el exito
            return reserva  # Retorna la reserva ya cancelada
        except SoftwareFJError as error:  # Complemento: reserva inexistente, ya cancelada o ya procesada
            self.registrar_error("Cancelacion de reserva", error)  # Lo deja en el log
            raise  # Lo propaga
        finally:  # Complemento: se ejecuta siempre, haya o no error
            estado = reserva.estado if reserva else "NO ENCONTRADA"  # Estado final de la reserva
            log.info("Fin del intento de cancelacion #%s (estado: %s)", id_reserva, estado)  # Deja constancia

    def listar_reservas(self):  # Devuelve todas las reservas almacenadas
        """Lista de reservas creadas."""
        return self.reservas  # Retorna la lista de reservas

    def obtener_inventario(self) -> dict:  # Devuelve el estado actual del inventario de equipos
        """Diccionario equipo -> unidades disponibles."""
        return self.inventario_equipos  # Retorna el diccionario de equipos y cantidades disponibles

    def resumen(self) -> str:  # Complemento: resumen general del sistema
        """Totales de clientes, reservas, ingresos y errores controlados."""
        procesadas = [r for r in self.reservas if r.estado == "PROCESADA"]  # Reservas cobradas
        ingresos = sum(r.total for r in procesadas)  # Suma de lo cobrado
        return (f"Clientes: {len(self.clientes)} | Reservas: {len(self.reservas)} | "  # Arma el texto del resumen
                f"Procesadas: {len(procesadas)} | Ingresos: ${ingresos:,.0f} | "
                f"Errores controlados: {self.errores_controlados}")
