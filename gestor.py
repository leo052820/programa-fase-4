from modelo import Cliente, Servicio, Reserva, AlquilerEquipo  # Importa las clases del modelo de dominio

class GestorEmpresa:  # Clase encargada de gestionar clientes, inventario y reservas
    def __init__(self):  # Constructor que inicializa las estructuras de datos en memoria
        self.clientes = {}  # Diccionario para almacenar clientes usando el documento como clave
        self.reservas = []  # Lista para guardar el historial de reservas creadas
        self.contador_reservas = 1  # Secuencia numerica para asignar IDs unicos a cada reserva
        self.inventario_equipos = {  # Diccionario con el stock inicial disponible por tipo de equipo
            "Laptop": 10,  # 10 laptops disponibles inicialmente
            "Tablet": 8,  # 8 tablets disponibles inicialmente
            "Camara": 5,  # 5 camaras disponibles inicialmente
            "Kit VR": 3  # 3 kits de realidad virtual disponibles inicialmente
        }

    def registrar_cliente(self, documento: str, nombre: str, correo: str) -> Cliente:  # Registra un nuevo cliente
        if documento in self.clientes:  # Comprueba si ya existe un cliente con ese documento
            raise ValueError(f"Ya existe un cliente registrado con el documento {documento}.")  # Lanza error si esta duplicado
        cliente = Cliente(documento, nombre, correo)  # Crea la instancia de Cliente
        self.clientes[documento] = cliente  # Almacena el cliente en el diccionario usando su documento
        return cliente  # Retorna el cliente recien registrado

    def buscar_cliente(self, documento: str) -> Cliente:  # Busca un cliente por su numero de documento
        cliente = self.clientes.get(documento)  # Obtiene el cliente si existe o None si no se encuentra
        if not cliente:  # Si no se encontro el cliente
            raise ValueError(f"No se encontro ningun cliente con documento {documento}.")  # Lanza error informativo
        return cliente  # Retorna el objeto Cliente encontrado

    def crear_reserva(self, documento_cliente: str, servicio: Servicio) -> Reserva:  # Crea y registra una reserva
        cliente = self.buscar_cliente(documento_cliente)  # Valida que el cliente exista y obtiene su objeto

        if isinstance(servicio, AlquilerEquipo):  # Verifica si el servicio solicitado es alquiler de equipo
            disponibles = self.inventario_equipos.get(servicio.nombre_equipo, 0)  # Consulta unidades disponibles del equipo
            if servicio.cantidad > disponibles:  # Revisa si hay suficiente stock para cubrir la solicitud
                raise ValueError(  # Lanza error si no hay suficientes unidades disponibles
                    f"Stock insuficiente para '{servicio.nombre_equipo}'. "  # Indica el equipo con falta de stock
                    f"Disponibles: {disponibles}, Solicitados: {servicio.cantidad}."  # Muestra disponibilidad vs solicitado
                )
            self.inventario_equipos[servicio.nombre_equipo] -= servicio.cantidad  # Descuenta las unidades alquiladas del inventario

        nueva_reserva = Reserva(self.contador_reservas, cliente, servicio)  # Instancia la nueva reserva con su ID
        self.reservas.append(nueva_reserva)  # Agrega la reserva a la lista general de reservas
        self.contador_reservas += 1  # Incrementa el contador para la siguiente reserva
        return nueva_reserva  # Retorna la reserva creada

    def cancelar_reserva(self, id_reserva: int) -> Reserva:  # Cancela una reserva existente por su ID
        for reserva in self.reservas:  # Recorre todas las reservas registradas
            if reserva.id_reserva == id_reserva:  # Busca coincidencia con el ID solicitado
                reserva.cancelar()  # Cambia el estado de la reserva a CANCELADA
                if isinstance(reserva.servicio, AlquilerEquipo):  # Si la reserva era de alquiler de equipo
                    equipo = reserva.servicio.nombre_equipo  # Obtiene el nombre del equipo alquilado
                    self.inventario_equipos[equipo] += reserva.servicio.cantidad  # Devuelve las unidades al inventario disponible
                return reserva  # Retorna la reserva ya cancelada
        raise ValueError(f"No existe una reserva con el ID #{id_reserva}.")  # Lanza error si no se hallo el ID

    def listar_reservas(self):  # Devuelve todas las reservas almacenadas
        return self.reservas  # Retorna la lista de reservas

    def obtener_inventario(self) -> dict:  # Devuelve el estado actual del inventario de equipos
        return self.inventario_equipos  # Retorna el diccionario de equipos y cantidades disponibles