"""
modelo.py
Clases del dominio: entidad abstracta, cliente, servicios y reserva.

Version inicial: Jose Leonardo Lopez Rangel (clientes, servicios, tarifas,
proyector, limite de 4 horas en asesorias y reserva con cancelacion).
Complemento: Jimena Jacome Contreras (clase abstracta general, validaciones
y encapsulacion del cliente, excepciones personalizadas, metodos sobrescritos
de validacion, metodos sobrecargados para impuestos y descuentos, y
confirmacion y procesamiento de reservas).
"""

import re  # Complemento: expresiones regulares para validar formatos
from abc import ABC, abstractmethod  # Importa ABC y abstractmethod para crear clases abstractas (plantillas base)
from datetime import datetime  # Complemento: fecha de creacion de cada entidad
from functools import singledispatchmethod  # Complemento: sobrecarga de metodos segun el tipo del argumento
from excepciones import (ValidacionError, ParametroFaltanteError, CalculoInconsistenteError,
                         OperacionNoPermitidaError, ReservaError, SoftwareFJError)  # Complemento: errores propios

IVA = 0.19  # Complemento: impuesto por defecto (19 %)
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")  # Complemento: formato usuario@dominio.ext
PATRON_DOCUMENTO = re.compile(r"^\d{4,12}$")  # Complemento: documento de 4 a 12 digitos


class EntidadBase(ABC):  # Complemento: clase abstracta que representa cualquier entidad general del sistema
    """Entidad general: tiene fecha de creacion y debe saber describirse y validarse."""

    def __init__(self):  # Constructor comun a todas las entidades
        self._fecha_creacion = datetime.now()  # Guarda el momento en que se creo la entidad

    @property
    def fecha_creacion(self):  # Fecha de creacion de solo lectura (encapsulacion)
        """Fecha y hora en que se creo la entidad."""
        return self._fecha_creacion  # Devuelve la fecha guardada

    @abstractmethod  # Las clases hijas deben implementarlo
    def obtener_detalle(self) -> str:
        """Devuelve una descripcion en texto de la entidad."""

    @abstractmethod  # Las clases hijas deben implementarlo
    def validar(self):
        """Verifica que la entidad sea consistente; lanza una excepcion si no lo es."""


class Cliente(EntidadBase):  # Define la clase que representa a un cliente de la empresa
    """Cliente con datos personales encapsulados y validados."""

    def __init__(self, documento: str, nombre: str, correo: str):  # Constructor que inicializa los datos del cliente
        super().__init__()  # Complemento: registra la fecha de creacion
        self.documento = documento  # Guarda el numero de identificacion unico del cliente
        self.nombre = nombre  # Guarda el nombre completo del cliente
        self.correo = correo  # Guarda el correo electronico del cliente

    # ----- Complemento: encapsulacion con propiedades que validan cada dato -----
    @property
    def documento(self):  # Lectura del documento
        """Numero de identificacion del cliente."""
        return self.__documento  # Atributo privado (doble guion bajo)

    @documento.setter
    def documento(self, valor):  # Escritura del documento con validacion
        if valor is None or not str(valor).strip():  # El documento es obligatorio
            raise ParametroFaltanteError("documento")  # Lanza error si falta
        valor = str(valor).strip()  # Lo convierte a texto sin espacios
        if not PATRON_DOCUMENTO.match(valor):  # Solo digitos, de 4 a 12
            raise ValidacionError("documento", "debe tener solo numeros (4 a 12 digitos)")  # Formato invalido
        self.__documento = valor  # Guarda el documento validado

    @property
    def nombre(self):  # Lectura del nombre
        """Nombre completo del cliente."""
        return self.__nombre  # Atributo privado

    @nombre.setter
    def nombre(self, valor):  # Escritura del nombre con validacion
        if valor is None or not str(valor).strip():  # El nombre es obligatorio
            raise ParametroFaltanteError("nombre")  # Lanza error si falta
        valor = str(valor).strip()  # Quita espacios al inicio y al final
        if len(valor) < 3 or not all(c.isalpha() or c.isspace() for c in valor):  # Solo letras y espacios
            raise ValidacionError("nombre", "debe tener al menos 3 letras y no incluir numeros ni simbolos")
        self.__nombre = valor.title()  # Guarda el nombre con mayuscula inicial

    @property
    def correo(self):  # Lectura del correo
        """Correo electronico del cliente."""
        return self.__correo  # Atributo privado

    @correo.setter
    def correo(self, valor):  # Escritura del correo con validacion
        if valor is None or not str(valor).strip():  # El correo es obligatorio
            raise ParametroFaltanteError("correo")  # Lanza error si falta
        valor = str(valor).strip().lower()  # Normaliza a minusculas
        if not PATRON_CORREO.match(valor):  # Verifica el formato usuario@dominio.ext
            raise ValidacionError("correo", f"formato invalido: {valor}")  # Formato invalido
        self.__correo = valor  # Guarda el correo validado

    def validar(self):  # Complemento: revalida todos los datos del cliente
        """Vuelve a pasar cada dato por su validacion."""
        self.documento, self.nombre, self.correo = self.documento, self.nombre, self.correo  # Usa los setters
        return True  # Si no hubo excepcion, el cliente es valido

    def obtener_detalle(self) -> str:  # Complemento: descripcion del cliente
        """Devuelve los datos del cliente en una linea."""
        return str(self)  # Reutiliza el formato de __str__

    def __str__(self):  # Define como se imprimira un objeto Cliente en texto legible
        return f"{self.nombre} (ID: {self.documento} | {self.correo})"  # Retorna cadena formateada con datos del cliente


class Servicio(EntidadBase):  # Clase abstracta base que heredan todos los servicios ofrecidos
    """Servicio general medido en horas."""

    def __init__(self, horas: int):  # Constructor comun para cualquier servicio medido en horas
        super().__init__()  # Complemento: registra la fecha de creacion
        if horas is None:  # Complemento: las horas son obligatorias
            raise ParametroFaltanteError("horas")  # Lanza error si falta el dato
        if not isinstance(horas, int) or isinstance(horas, bool):  # Complemento: deben ser un numero entero
            raise ValidacionError("horas", "deben ser un numero entero")  # Lanza error si no es entero
        if horas <= 0:  # Verifica que la duracion en horas sea positiva
            raise ValidacionError("horas", "La duracion debe ser mayor a 0 horas.")  # Lanza error si las horas son cero o negativas
        self.horas = horas  # Guarda la cantidad de horas solicitadas para el servicio

    @abstractmethod  # Marca este metodo como obligatorio en las clases hijas
    def calcular_precio(self) -> float:  # Firma del metodo para calcular el costo total del servicio
        """Precio del servicio sin impuestos ni descuentos."""

    @abstractmethod  # Marca este metodo como obligatorio en las clases hijas
    def obtener_detalle(self) -> str:  # Firma del metodo para describir las caracteristicas del servicio
        """Descripcion del servicio."""

    @abstractmethod  # Complemento: cada servicio valida sus propios parametros
    def validar_parametros(self):
        """Valida los datos propios del servicio; lanza ValidacionError si algo no cumple."""

    def validar(self):  # Complemento: validacion general del servicio
        """Revalida el servicio con sus reglas propias."""
        self.validar_parametros()  # Llama a la validacion sobrescrita en cada servicio (polimorfismo)
        return True  # Si no hubo excepcion, el servicio es valido

    # ----- Complemento: calculo con parametros opcionales (sobrecarga) -----
    def calcular_costo(self, impuesto=None, descuento=None, rebaja=None) -> float:
        """Precio con impuesto y descuento opcionales (de 0 a 1) y rebaja opcional en pesos."""
        precio = self.calcular_precio()  # Precio base calculado por cada servicio
        if descuento is not None:  # Si se pidio descuento porcentual...
            if not 0 <= descuento < 1:  # ...debe estar entre 0 % y 99 %
                raise ValidacionError("descuento", "debe estar entre 0 y 1")  # Descuento invalido
            precio *= (1 - descuento)  # Aplica el descuento
        if rebaja is not None:  # Si se pidio una rebaja fija en pesos...
            precio -= rebaja  # ...se resta del precio
        if impuesto is not None:  # Si se pidio impuesto...
            if not 0 <= impuesto < 1:  # ...debe estar entre 0 % y 99 %
                raise ValidacionError("impuesto", "debe estar entre 0 y 1")  # Impuesto invalido
            precio *= (1 + impuesto)  # Aplica el impuesto
        if precio <= 0:  # Un precio cero o negativo no tiene sentido
            raise CalculoInconsistenteError(f"Precio invalido (${precio:,.0f}) para {self.obtener_detalle()}")
        return round(precio, 2)  # Redondea a dos decimales

    @singledispatchmethod
    def cotizar(self, opcion):  # Complemento: version por defecto (tipo no soportado)
        """Cotiza el servicio; acepta un entero (horas), una lista (bloques) o un diccionario (opciones)."""
        raise ValidacionError("cotizacion", f"tipo no soportado: {type(opcion).__name__}")  # Tipo invalido

    @cotizar.register
    def _(self, opcion: int):  # Variante 1: precio con IVA para otra cantidad de horas
        valor_hora = self.calcular_precio() / self.horas  # Valor de una hora del servicio
        return round(valor_hora * opcion * (1 + IVA), 2)  # No modifica las horas del servicio

    @cotizar.register
    def _(self, opcion: list):  # Variante 2: suma de varios bloques de horas
        return round(sum(self.cotizar(horas) for horas in opcion), 2)  # Cotiza cada bloque y suma

    @cotizar.register
    def _(self, opcion: dict):  # Variante 3: diccionario con impuesto, descuento o rebaja
        return self.calcular_costo(impuesto=opcion.get("impuesto", IVA),  # Pasa las opciones recibidas
                                   descuento=opcion.get("descuento"),
                                   rebaja=opcion.get("rebaja"))


class ReservaSala(Servicio):  # Subclase de Servicio para el alquiler de salas
    """Reserva de salas con proyector opcional."""

    TARIFA_HORA_BASE = 50000  # Costo base por hora de uso de la sala
    TARIFA_PROYECTOR_HORA = 15000  # Costo adicional por hora si se solicita proyector
    MAXIMO_HORAS = 12  # Complemento: una sala se reserva maximo 12 horas

    def __init__(self, horas: int, num_personas: int, con_proyector: bool):  # Constructor especifico de ReservaSala
        super().__init__(horas)  # Llama al constructor de Servicio para validar y asignar 'self.horas'
        self.num_personas = num_personas  # Guarda la cantidad de personas que usaran la sala
        self.con_proyector = con_proyector  # Guarda booleano (True/False) indicando si requiere proyector
        self.validar_parametros()  # Complemento: valida los datos propios de la sala

    def validar_parametros(self):  # Complemento: metodo sobrescrito con las reglas de la sala
        """Valida el maximo de horas y la cantidad de personas."""
        if self.horas > self.MAXIMO_HORAS:  # No mas de 12 horas
            raise ValidacionError("horas", f"una sala se reserva maximo {self.MAXIMO_HORAS} horas")
        if not isinstance(self.num_personas, int) or self.num_personas <= 0:  # Comprueba que haya al menos una persona en la sala
            raise ValidacionError("personas", "La cantidad de personas debe ser mayor a 0.")  # Numero de personas invalido

    def calcular_precio(self) -> float:  # Calcula el precio total de la reserva de sala
        total = self.horas * self.TARIFA_HORA_BASE  # Multiplica horas por tarifa base de la sala
        if self.con_proyector:  # Si el cliente solicito proyector
            total += self.horas * self.TARIFA_PROYECTOR_HORA  # Suma el costo del proyector segun las horas
        return float(total)  # Devuelve el valor total como numero decimal (float)

    def obtener_detalle(self) -> str:  # Genera un resumen descriptivo de la reserva de sala
        proyector_txt = "Con proyector" if self.con_proyector else "Sin proyector"  # Traduce booleano a texto legible
        return f"Reserva de Sala ({self.horas}h, {self.num_personas} personas, {proyector_txt})"  # Retorna detalle formateado


class AlquilerEquipo(Servicio):  # Subclase de Servicio para el alquiler de equipos tecnologicos
    """Alquiler de equipos por hora y por unidad."""

    TARIFA_UNIDAD_HORA = 20000  # Costo por cada equipo alquilado durante una hora
    MAXIMO_HORAS = 72  # Complemento: un equipo se alquila maximo 72 horas

    def __init__(self, horas: int, nombre_equipo: str, cantidad: int):  # Constructor especifico de AlquilerEquipo
        super().__init__(horas)  # Valida y guarda 'self.horas' desde la clase padre
        self.nombre_equipo = nombre_equipo  # Guarda el nombre del equipo tecnologico (ej. Laptop)
        self.cantidad = cantidad  # Guarda cuantas unidades se desean alquilar
        self.validar_parametros()  # Complemento: valida los datos propios del alquiler

    def validar_parametros(self):  # Complemento: metodo sobrescrito con las reglas del alquiler
        """Valida el maximo de horas, el nombre del equipo y la cantidad."""
        if self.horas > self.MAXIMO_HORAS:  # No mas de 72 horas
            raise ValidacionError("horas", f"un equipo se alquila maximo {self.MAXIMO_HORAS} horas")
        if not self.nombre_equipo:  # El nombre del equipo es obligatorio
            raise ParametroFaltanteError("nombre del equipo")  # Lanza error si falta
        if not isinstance(self.cantidad, int) or self.cantidad <= 0:  # Verifica que se solicite al menos una unidad del equipo
            raise ValidacionError("cantidad", "La cantidad de equipos debe ser mayor a 0.")  # Cantidad invalida

    def calcular_precio(self) -> float:  # Calcula el costo total del alquiler de equipos
        return float(self.horas * self.cantidad * self.TARIFA_UNIDAD_HORA)  # Horas * unidades * tarifa por unidad/hora

    def obtener_detalle(self) -> str:  # Genera un resumen descriptivo del alquiler de equipos
        return f"Alquiler de Equipo: {self.cantidad}x {self.nombre_equipo} ({self.horas}h)"  # Retorna detalle formateado


class AsesoriaEspecializada(Servicio):  # Subclase de Servicio para asesorias informaticas
    """Asesoria virtual o presencial de maximo 4 horas."""

    TARIFA_HORA_VIRTUAL = 70000  # Tarifa por hora para asesorias en modalidad virtual
    TARIFA_HORA_PRESENCIAL = 95000  # Tarifa por hora para asesorias en modalidad presencial

    def __init__(self, horas: int, modalidad: str, tema: str):  # Constructor especifico de AsesoriaEspecializada
        super().__init__(horas)  # Valida y guarda 'self.horas' desde la clase padre
        modalidad_limpia = str(modalidad).strip().lower()  # Quita espacios extremos y convierte a minusculas
        self.modalidad = modalidad_limpia  # Guarda la modalidad normalizada ('virtual' o 'presencial')
        self.tema = tema  # Guarda el tema o especialidad de la asesoria
        self.validar_parametros()  # Complemento: valida los datos propios de la asesoria

    def validar_parametros(self):  # Complemento: metodo sobrescrito con las reglas de la asesoria
        """Valida el maximo de 4 horas, la modalidad y el tema."""
        if self.horas > 4:  # Aplica la regla de negocio: maximo 4 horas de asesoria
            raise ValidacionError("horas", "Las asesorias tienen una duracion maxima de 4 horas.")  # Supera 4 horas
        if self.modalidad not in ["virtual", "presencial"]:  # Verifica que la modalidad sea valida
            raise ValidacionError("modalidad", "La modalidad debe ser 'virtual' o 'presencial'.")  # Modalidad no existe
        if not self.tema:  # El tema es obligatorio
            raise ParametroFaltanteError("tema de la asesoria")  # Lanza error si falta

    def calcular_precio(self) -> float:  # Calcula el valor total de la asesoria segun modalidad y horas
        tarifa = self.TARIFA_HORA_VIRTUAL if self.modalidad == "virtual" else self.TARIFA_HORA_PRESENCIAL  # Elige tarifa por hora
        return float(self.horas * tarifa)  # Multiplica horas por tarifa correspondiente y retorna float

    def obtener_detalle(self) -> str:  # Genera un resumen descriptivo de la asesoria
        return f"Asesoria {self.modalidad.capitalize()} en '{self.tema}' ({self.horas}h)"  # Retorna detalle formateado


class Reserva(EntidadBase):  # Clase que vincula un cliente, un servicio, un costo total y un estado
    """Reserva con estados: ACTIVA -> CONFIRMADA -> PROCESADA, o CANCELADA."""

    def __init__(self, id_reserva: int, cliente: Cliente, servicio: Servicio):  # Constructor de Reserva
        super().__init__()  # Complemento: registra la fecha de creacion
        if not isinstance(cliente, Cliente):  # Complemento: debe recibir un objeto Cliente
            raise ReservaError("La reserva necesita un cliente valido")  # Lanza error si no lo es
        if not isinstance(servicio, Servicio):  # Complemento: debe recibir un objeto Servicio
            raise ReservaError("La reserva necesita un servicio valido")  # Lanza error si no lo es
        self.id_reserva = id_reserva  # Asigna el identificador numerico unico de la reserva
        self.cliente = cliente  # Guarda la referencia al objeto Cliente que realiza la reserva
        self.servicio = servicio  # Guarda la referencia al objeto Servicio contratado
        self.total = servicio.calcular_precio()  # Calcula y guarda el precio final de la reserva al crearla
        self.estado = "ACTIVA"  # Inicializa el estado de la reserva como activa

    def confirmar(self):  # Complemento: ACTIVA -> CONFIRMADA
        """Confirma una reserva activa."""
        if self.estado != "ACTIVA":  # Solo se confirma una reserva activa
            raise OperacionNoPermitidaError(self.estado, "confirmar")  # Lanza error si no lo esta
        self.estado = "CONFIRMADA"  # Actualiza el estado a confirmada

    def procesar(self, descuento=None):  # Complemento: CONFIRMADA -> PROCESADA (cobro final con IVA)
        """Calcula el valor final con IVA y descuento opcional, y finaliza la reserva."""
        if self.estado != "CONFIRMADA":  # Solo se procesa lo que esta confirmado
            raise OperacionNoPermitidaError(self.estado, "procesar")  # Lanza error si no lo esta
        try:  # El calculo puede fallar por un descuento invalido
            total = self.servicio.calcular_costo(impuesto=IVA, descuento=descuento)  # Calcula el cobro final
        except SoftwareFJError as error:  # Error de validacion o de calculo
            raise ReservaError(f"No se pudo procesar la reserva #{self.id_reserva}") from error  # Encadenamiento
        self.total = total  # Actualiza el total con el valor cobrado
        self.estado = "PROCESADA"  # Actualiza el estado a procesada
        return total  # Devuelve el valor cobrado

    def cancelar(self):  # Cambia el estado de la reserva a cancelada
        """Cancela una reserva que aun no se ha cobrado."""
        if self.estado == "CANCELADA":  # Verifica si la reserva ya habia sido cancelada previamente
            raise OperacionNoPermitidaError(self.estado, "cancelar")  # Evita cancelar dos veces la misma reserva
        if self.estado == "PROCESADA":  # Complemento: una reserva cobrada ya no se cancela
            raise OperacionNoPermitidaError(self.estado, "cancelar")  # Lanza error
        self.estado = "CANCELADA"  # Actualiza el estado a cancelada

    def validar(self):  # Complemento: revalida cliente y servicio de la reserva
        """Comprueba que el cliente y el servicio sigan siendo validos."""
        return self.cliente.validar() and self.servicio.validar()  # Valida ambos objetos

    def obtener_detalle(self) -> str:  # Complemento: descripcion de la reserva
        """Devuelve los datos de la reserva en una linea."""
        return str(self)  # Reutiliza el formato de __str__

    def __str__(self):  # Define como se muestra una reserva al imprimirla en consola
        return (f"[Reserva #{self.id_reserva}] Estado: {self.estado} | "  # Muestra ID y estado
                f"Cliente: {self.cliente.nombre} | {self.servicio.obtener_detalle()} | "  # Muestra cliente y detalle del servicio
                f"Total: ${self.total:,.0f}")  # Muestra el total formateado con separadores de miles
