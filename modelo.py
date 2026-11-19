from abc import ABC, abstractmethod  # Importa ABC y abstractmethod para crear clases abstractas (plantillas base)

class Cliente:  # Define la clase que representa a un cliente de la empresa
    def __init__(self, documento: str, nombre: str, correo: str):  # Constructor que inicializa los datos del cliente
        self.documento = documento  # Guarda el numero de identificacion unico del cliente
        self.nombre = nombre  # Guarda el nombre completo del cliente
        self.correo = correo  # Guarda el correo electronico del cliente

    def __str__(self):  # Define como se imprimira un objeto Cliente en texto legible
        return f"{self.nombre} (ID: {self.documento} | {self.correo})"  # Retorna cadena formateada con datos del cliente


class Servicio(ABC):  # Clase abstracta base que heredan todos los servicios ofrecidos
    def __init__(self, horas: int):  # Constructor comun para cualquier servicio medido en horas
        if horas <= 0:  # Verifica que la duracion en horas sea positiva
            raise ValueError("La duracion debe ser mayor a 0 horas.")  # Lanza error si las horas son cero o negativas
        self.horas = horas  # Guarda la cantidad de horas solicitadas para el servicio

    @abstractmethod  # Marca este metodo como obligatorio en las clases hijas
    def calcular_precio(self) -> float:  # Firma del metodo para calcular el costo total del servicio
        pass  # Sin implementacion aqui porque cada servicio calcula su precio distinto

    @abstractmethod  # Marca este metodo como obligatorio en las clases hijas
    def obtener_detalle(self) -> str:  # Firma del metodo para describir las caracteristicas del servicio
        pass  # Sin implementacion aqui porque cada servicio detalla distintos campos


class ReservaSala(Servicio):  # Subclase de Servicio para el alquiler de salas
    TARIFA_HORA_BASE = 50000  # Costo base por hora de uso de la sala
    TARIFA_PROYECTOR_HORA = 15000  # Costo adicional por hora si se solicita proyector

    def __init__(self, horas: int, num_personas: int, con_proyector: bool):  # Constructor especifico de ReservaSala
        super().__init__(horas)  # Llama al constructor de Servicio para validar y asignar 'self.horas'
        if num_personas <= 0:  # Comprueba que haya al menos una persona en la sala
            raise ValueError("La cantidad de personas debe ser mayor a 0.")  # Lanza error si el numero de personas es invalido
        self.num_personas = num_personas  # Guarda la cantidad de personas que usaran la sala
        self.con_proyector = con_proyector  # Guarda booleano (True/False) indicando si requiere proyector

    def calcular_precio(self) -> float:  # Calcula el precio total de la reserva de sala
        total = self.horas * self.TARIFA_HORA_BASE  # Multiplica horas por tarifa base de la sala
        if self.con_proyector:  # Si el cliente solicito proyector
            total += self.horas * self.TARIFA_PROYECTOR_HORA  # Suma el costo del proyector segun las horas
        return float(total)  # Devuelve el valor total como numero decimal (float)

    def obtener_detalle(self) -> str:  # Genera un resumen descriptivo de la reserva de sala
        proyector_txt = "Con proyector" if self.con_proyector else "Sin proyector"  # Traduce booleano a texto legible
        return f"Reserva de Sala ({self.horas}h, {self.num_personas} personas, {proyector_txt})"  # Retorna detalle formateado


class AlquilerEquipo(Servicio):  # Subclase de Servicio para el alquiler de equipos tecnologicos
    TARIFA_UNIDAD_HORA = 20000  # Costo por cada equipo alquilado durante una hora

    def __init__(self, horas: int, nombre_equipo: str, cantidad: int):  # Constructor especifico de AlquilerEquipo
        super().__init__(horas)  # Valida y guarda 'self.horas' desde la clase padre
        if cantidad <= 0:  # Verifica que se solicite al menos una unidad del equipo
            raise ValueError("La cantidad de equipos debe ser mayor a 0.")  # Lanza error si la cantidad es menor o igual a 0
        self.nombre_equipo = nombre_equipo  # Guarda el nombre del equipo tecnologico (ej. Laptop)
        self.cantidad = cantidad  # Guarda cuantas unidades se desean alquilar

    def calcular_precio(self) -> float:  # Calcula el costo total del alquiler de equipos
        return float(self.horas * self.cantidad * self.TARIFA_UNIDAD_HORA)  # Horas * unidades * tarifa por unidad/hora

    def obtener_detalle(self) -> str:  # Genera un resumen descriptivo del alquiler de equipos
        return f"Alquiler de Equipo: {self.cantidad}x {self.nombre_equipo} ({self.horas}h)"  # Retorna detalle formateado


class AsesoriaEspecializada(Servicio):  # Subclase de Servicio para asesorias informaticas
    TARIFA_HORA_VIRTUAL = 70000  # Tarifa por hora para asesorias en modalidad virtual
    TARIFA_HORA_PRESENCIAL = 95000  # Tarifa por hora para asesorias en modalidad presencial

    def __init__(self, horas: int, modalidad: str, tema: str):  # Constructor especifico de AsesoriaEspecializada
        super().__init__(horas)  # Valida y guarda 'self.horas' desde la clase padre
        if horas > 4:  # Aplica la regla de negocio: maximo 4 horas de asesoria
            raise ValueError("Las asesorias tienen una duracion maxima de 4 horas.")  # Lanza error si supera 4 horas
        modalidad_limpia = modalidad.strip().lower()  # Quita espacios extremos y convierte a minusculas
        if modalidad_limpia not in ["virtual", "presencial"]:  # Verifica que la modalidad sea valida
            raise ValueError("La modalidad debe ser 'virtual' o 'presencial'.")  # Lanza error si la modalidad no existe
        self.modalidad = modalidad_limpia  # Guarda la modalidad normalizada ('virtual' o 'presencial')
        self.tema = tema  # Guarda el tema o especialidad de la asesoria

    def calcular_precio(self) -> float:  # Calcula el valor total de la asesoria segun modalidad y horas
        tarifa = self.TARIFA_HORA_VIRTUAL if self.modalidad == "virtual" else self.TARIFA_HORA_PRESENCIAL  # Elige tarifa por hora
        return float(self.horas * tarifa)  # Multiplica horas por tarifa correspondiente y retorna float

    def obtener_detalle(self) -> str:  # Genera un resumen descriptivo de la asesoria
        return f"Asesoria {self.modalidad.capitalize()} en '{self.tema}' ({self.horas}h)"  # Retorna detalle formateado


class Reserva:  # Clase que vincula un cliente, un servicio, un costo total y un estado
    def __init__(self, id_reserva: int, cliente: Cliente, servicio: Servicio):  # Constructor de Reserva
        self.id_reserva = id_reserva  # Asigna el identificador numerico unico de la reserva
        self.cliente = cliente  # Guarda la referencia al objeto Cliente que realiza la reserva
        self.servicio = servicio  # Guarda la referencia al objeto Servicio contratado
        self.total = servicio.calcular_precio()  # Calcula y guarda el precio final de la reserva al crearla
        self.estado = "ACTIVA"  # Inicializa el estado de la reserva como activa

    def cancelar(self):  # Cambia el estado de la reserva a cancelada
        if self.estado == "CANCELADA":  # Verifica si la reserva ya habia sido cancelada previamente
            raise ValueError("La reserva ya se encuentra cancelada.")  # Evita cancelar dos veces la misma reserva
        self.estado = "CANCELADA"  # Actualiza el estado a cancelada

    def __str__(self):  # Define como se muestra una reserva al imprimirla en consola
        return (f"[Reserva #{self.id_reserva}] Estado: {self.estado} | "  # Muestra ID y estado
                f"Cliente: {self.cliente.nombre} | {self.servicio.obtener_detalle()} | "  # Muestra cliente y detalle del servicio
                f"Total: ${self.total:,.0f}")  # Muestra el total formateado con separadores de miles