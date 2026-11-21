"""
servicios.py
Clase abstracta Servicio y tres servicios especializados:
ReservaSala, AlquilerEquipo y Asesoria.

Cada servicio sobrescribe calcular_costo(), describir() y
validar_parametros() (polimorfismo). El cálculo de costos tiene
varias variantes (sobrecarga):
  - calcular_costo(horas)                          -> costo base
  - calcular_costo(horas, impuesto=0.19)           -> con impuesto
  - calcular_costo(horas, descuento=0.10)          -> con descuento
  - calcular_costo(horas, impuesto=..., descuento=...) -> ambos
  - calcular_costo(horas, rebaja=50000)            -> con rebaja fija en pesos
  - cotizar(horas) / cotizar([h1, h2, ...]) / cotizar({"horas": h, ...})
    -> la misma operación aceptando un número, una lista o un diccionario
"""

from abc import abstractmethod                         # Para declarar métodos abstractos
from functools import singledispatchmethod             # Sobrecarga de métodos según el tipo del argumento
from .entidad import EntidadBase                       # Clase abstracta base
from .excepciones import (ValidacionError, ParametroFaltanteError,
                          CalculoInconsistenteError)   # Errores que pueden lanzar los servicios

IVA = 0.19                                             # Impuesto por defecto (19 %)


class Servicio(EntidadBase):                           # Clase abstracta de servicios
    """Servicio general ofrecido por Software FJ."""

    def __init__(self, nombre, tarifa_hora, disponible=True):
        """Valida y guarda los datos comunes a todos los servicios."""
        if not nombre:                                 # El nombre es obligatorio
            raise ParametroFaltanteError("nombre del servicio")
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:   # Tarifa numérica positiva
            raise ValidacionError("tarifa_hora", "debe ser un número mayor que cero")
        self._nombre = nombre                          # Atributo protegido: lo usan las clases hijas
        self._tarifa_hora = float(tarifa_hora)         # Se guarda como número decimal
        self._disponible = bool(disponible)            # Indica si el servicio se puede reservar
        super().__init__("SRV")                        # Solo si todo es válido se asigna el ID

    @property
    def nombre(self):
        """Lectura del nombre."""
        return self._nombre

    @property
    def tarifa_hora(self):
        """Lectura de la tarifa."""
        return self._tarifa_hora

    @property
    def disponible(self):
        """Lectura de la disponibilidad."""
        return self._disponible

    def cambiar_disponibilidad(self, disponible):
        """Permite habilitar o deshabilitar el servicio."""
        self._disponible = bool(disponible)

    # ----- Métodos que cada servicio debe sobrescribir -----
    @abstractmethod
    def costo_base(self, horas):
        """Costo sin impuestos ni descuentos para la cantidad de horas indicada."""

    @abstractmethod
    def validar_parametros(self, horas):
        """Valida la duración solicitada según las reglas del servicio."""

    # ----- Cálculo de costos con parámetros opcionales (sobrecarga) -----
    def calcular_costo(self, horas, impuesto=None, descuento=None, rebaja=None):
        """Calcula el costo; impuesto y descuento (0 a 1) y rebaja en pesos son opcionales."""
        self.validar_parametros(horas)                 # Primero valida la duración
        costo = self.costo_base(horas)                 # Costo sin ajustes (polimórfico)
        if descuento is not None:                      # Si se pidió descuento porcentual...
            if not 0 <= descuento < 1:                 # ...debe estar entre 0 % y 99 %
                raise ValidacionError("descuento", "debe estar entre 0 y 1")
            costo *= (1 - descuento)                   # Aplica el descuento
        if rebaja is not None:                         # Si se pidió una rebaja en pesos...
            costo -= rebaja                            # ...se resta del costo
        if impuesto is not None:                       # Si se pidió impuesto...
            if not 0 <= impuesto < 1:                  # ...debe estar entre 0 % y 99 %
                raise ValidacionError("impuesto", "debe estar entre 0 y 1")
            costo *= (1 + impuesto)                    # Aplica el impuesto
        if costo <= 0:                                 # Un costo cero o negativo no tiene sentido
            raise CalculoInconsistenteError(f"Costo inválido (${costo:,.2f}) para '{self.nombre}'")
        return round(costo, 2)                         # Redondea a dos decimales

    # ----- Sobrecarga según el tipo del argumento -----
    @singledispatchmethod
    def cotizar(self, duracion):
        """Versión por defecto: tipo no soportado."""
        raise ValidacionError("duracion", f"tipo no soportado: {type(duracion).__name__}")

    @cotizar.register
    def _(self, duracion: int):
        """Variante 1: un número entero de horas."""
        return self.calcular_costo(duracion, impuesto=IVA)

    @cotizar.register
    def _(self, duracion: float):
        """Variante 2: horas con decimales."""
        return self.calcular_costo(duracion, impuesto=IVA)

    @cotizar.register
    def _(self, duracion: list):
        """Variante 3: lista de bloques de horas."""
        return round(sum(self.cotizar(h) for h in duracion), 2)   # Suma la cotización de cada bloque

    @cotizar.register
    def _(self, duracion: dict):
        """Variante 4: diccionario con opciones."""
        if "horas" not in duracion:                    # La clave horas es obligatoria
            raise ParametroFaltanteError("horas")
        return self.calcular_costo(duracion["horas"],  # Pasa las opciones del diccionario
                                   impuesto=duracion.get("impuesto", IVA),
                                   descuento=duracion.get("descuento"),
                                   rebaja=duracion.get("rebaja"))

    def validar(self):
        """Validación general del servicio."""
        if self._tarifa_hora <= 0:                     # La tarifa debe seguir siendo positiva
            raise CalculoInconsistenteError("La tarifa del servicio no es válida")
        return True

    @staticmethod
    def _validar_horas(horas, minimo, maximo):
        """Regla común: horas numéricas dentro de un rango."""
        if horas is None:                              # La duración es obligatoria
            raise ParametroFaltanteError("horas")
        if not isinstance(horas, (int, float)) or isinstance(horas, bool):   # Debe ser numérica
            raise ValidacionError("horas", "debe ser un número")
        if not minimo <= horas <= maximo:              # Debe estar dentro del rango permitido
            raise ValidacionError("horas", f"debe estar entre {minimo} y {maximo}")


class ReservaSala(Servicio):                           # Servicio 1: reserva de salas
    """Reserva de salas de reuniones o capacitación, con proyector opcional."""

    TARIFA_PROYECTOR_HORA = 15000                      # Costo adicional por hora del proyector

    def __init__(self, nombre, tarifa_hora, capacidad, con_proyector=False, disponible=True):
        """Crea una sala con su capacidad máxima de personas y, si se pide, con proyector."""
        if not isinstance(capacidad, int) or capacidad <= 0:   # Capacidad entera positiva
            raise ValidacionError("capacidad", "debe ser un entero mayor que cero")
        self._capacidad = capacidad                    # Número de personas que caben en la sala
        self._con_proyector = bool(con_proyector)      # True si la sala incluye proyector
        super().__init__(nombre, tarifa_hora, disponible)   # Valida los datos comunes y asigna el ID

    def validar_parametros(self, horas):
        """Una sala se reserva de 1 a 12 horas."""
        self._validar_horas(horas, 1, 12)

    def costo_base(self, horas):
        """Salas grandes (más de 20) cuestan 20 % más; el proyector se cobra por hora."""
        recargo = 1.2 if self._capacidad > 20 else 1.0             # Recargo por tamaño
        proyector = self.TARIFA_PROYECTOR_HORA * horas if self._con_proyector else 0   # Adicional del proyector
        return self._tarifa_hora * horas * recargo + proyector

    def describir(self):
        """Descripción propia de una sala."""
        estado = "disponible" if self.disponible else "no disponible"
        proyector = "con proyector" if self._con_proyector else "sin proyector"   # Texto del proyector
        return (f"{self.id} | Sala '{self.nombre}' | {self._capacidad} personas, {proyector} | "
                f"${self.tarifa_hora:,.0f}/h | {estado}")


class AlquilerEquipo(Servicio):                        # Servicio 2: alquiler de equipos
    """Alquiler de equipos (portátiles, proyectores, etc.) por horas."""

    def __init__(self, nombre, tarifa_hora, cantidad, disponible=True):
        """Crea un alquiler con la cantidad de equipos solicitada."""
        if not isinstance(cantidad, int) or cantidad <= 0:     # Cantidad entera positiva
            raise ValidacionError("cantidad", "debe ser un entero mayor que cero")
        self._cantidad = cantidad                      # Número de unidades alquiladas
        super().__init__(nombre, tarifa_hora, disponible)   # Valida los datos comunes y asigna el ID

    @property
    def cantidad(self):
        """Número de unidades alquiladas (lo usa el control de inventario)."""
        return self._cantidad

    def validar_parametros(self, horas):
        """Un equipo se alquila de 1 a 72 horas."""
        self._validar_horas(horas, 1, 72)

    def costo_base(self, horas):
        """Tarifa por unidad y por hora, más un seguro fijo."""
        seguro = 15000 * self._cantidad                # Seguro de $15.000 por equipo
        return self._tarifa_hora * horas * self._cantidad + seguro

    def describir(self):
        """Descripción propia de un alquiler."""
        estado = "disponible" if self.disponible else "no disponible"
        return f"{self.id} | Equipo '{self.nombre}' x{self._cantidad} | ${self.tarifa_hora:,.0f}/h c/u | {estado}"


class Asesoria(Servicio):                              # Servicio 3: asesorías especializadas
    """Asesoría especializada; el nivel del asesor modifica la tarifa."""

    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}   # Multiplicador de tarifa por nivel

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="junior", disponible=True):
        """Crea una asesoría con su especialidad y el nivel del asesor."""
        if not especialidad:                           # La especialidad es obligatoria
            raise ParametroFaltanteError("especialidad")
        if nivel not in self.NIVELES:                  # El nivel debe ser uno de los definidos
            raise ValidacionError("nivel", f"debe ser uno de {list(self.NIVELES)}")
        self._especialidad = especialidad              # Área de la asesoría
        self._nivel = nivel                            # Nivel del asesor
        super().__init__(nombre, tarifa_hora, disponible)   # Valida los datos comunes y asigna el ID

    def validar_parametros(self, horas):
        """Una asesoría dura de 0.5 a 4 horas (máximo 4 horas)."""
        self._validar_horas(horas, 0.5, 4)

    def costo_base(self, horas):
        """Tarifa por hora según el nivel del asesor."""
        return self._tarifa_hora * horas * self.NIVELES[self._nivel]

    def describir(self):
        """Descripción propia de una asesoría."""
        estado = "disponible" if self.disponible else "no disponible"
        detalle = f"{self._especialidad}, {self._nivel}"   # Especialidad y nivel del asesor
        return f"{self.id} | Asesoría '{self.nombre}' ({detalle}) | ${self.tarifa_hora:,.0f}/h | {estado}"
