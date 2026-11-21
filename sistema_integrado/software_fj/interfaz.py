"""
interfaz.py
Menú interactivo por consola del sistema Software FJ.

Basado en el menú de la versión inicial del proyecto (José Leonardo
López Rangel) y adaptado al sistema con excepciones personalizadas,
validaciones e inventario de equipos.
"""

from .sistema import SistemaGestion                    # Lógica del sistema
from .registro import obtener_logger                   # Registro de eventos y errores

log = obtener_logger()                                 # Logger compartido del sistema

OPCIONES = (                                           # Texto de cada opción del menú
    "Registrar cliente",
    "Nueva reserva",
    "Confirmar y procesar una reserva",
    "Cancelar una reserva",
    "Ver reservas",
    "Ver inventario de equipos",
    "Ver resumen del sistema",
    "Salir",
)

TARIFAS = {                                            # Tarifas por hora de los servicios del menú
    "sala": 50000,                                     # Sala ($15.000/h adicionales con proyector)
    "equipo": 20000,                                   # Por unidad y por hora
    "asesoria": 70000,                                 # Base; el nivel del asesor la multiplica
}


def leer_entero(mensaje):
    """Pide un número entero; lanza ValueError si el usuario escribe otra cosa."""
    return int(input(mensaje).strip())                 # int() falla con letras o vacío


class SistemaInterfaz:
    """Interacción por consola con el usuario."""

    def __init__(self, sistema=None):
        """Recibe un SistemaGestion existente o crea uno nuevo."""
        self.sistema = sistema or SistemaGestion()     # Sistema sobre el que se opera
        self.acciones = (                              # Método que atiende cada opción del menú
            self.registrar_cliente,
            self.nueva_reserva,
            self.procesar_reserva,
            self.cancelar_reserva,
            self.ver_reservas,
            self.ver_inventario,
            self.ver_resumen,
        )

    def cargar_datos_iniciales(self):
        """Registra dos clientes de ejemplo para probar rápido."""
        print("\nCargando clientes de ejemplo...")
        self.sistema.registrar_cliente(nombre="Laura Gómez", documento="1001001",
                                       email="laura@correo.com")
        self.sistema.registrar_cliente(nombre="Carlos Ruiz", documento="1002002",
                                       email="carlos@correo.com")

    def iniciar(self):
        """Muestra el menú hasta que el usuario elija salir."""
        self.cargar_datos_iniciales()                  # Clientes de prueba (documentos 1001001 y 1002002)
        while True:                                    # Se repite hasta elegir "Salir"
            print("\n" + "=" * 45)
            print("   SOFTWARE FJ - MENÚ PRINCIPAL")
            print("=" * 45)
            for numero, texto in enumerate(OPCIONES, start=1):   # Muestra las opciones numeradas
                print(f"{numero}. {texto}")
            opcion = input(f"\nSeleccione una opción (1-{len(OPCIONES)}): ").strip()
            if opcion == str(len(OPCIONES)):           # Última opción: salir
                print("Saliendo del sistema. ¡Hasta pronto!")
                log.info("Menú interactivo cerrado por el usuario")
                break
            self.ejecutar(opcion)                      # Atiende la opción elegida

    def ejecutar(self, opcion):
        """Ejecuta una opción del menú sin permitir que un error cierre el programa."""
        try:
            accion = self.acciones[int(opcion) - 1]    # ValueError o IndexError si la opción no existe
            if int(opcion) < 1:                        # Evita que "0" tome la última acción
                raise IndexError(opcion)
        except (ValueError, IndexError):               # Opción escrita mal o fuera de rango
            print("   ✗ Opción no válida. Intente nuevamente.")
            return
        try:
            accion()                                   # Ejecuta la acción elegida
        except ValueError:                             # Letras donde se esperaba un número
            print("   ✗ ERROR: debe escribir un número entero.")
            log.warning("Entrada no numérica en la opción %s", opcion)
        except (KeyboardInterrupt, EOFError):          # El usuario interrumpe la captura
            print("\n   Operación cancelada por el usuario.")
        finally:                                       # Siempre: deja constancia de la opción usada
            log.info("Opción de menú atendida: %s", OPCIONES[int(opcion) - 1])

    # ------------------------------------------------------------------
    # Acciones del menú
    # ------------------------------------------------------------------
    def registrar_cliente(self):
        """Pide los datos de un cliente y lo registra."""
        print("\n--- REGISTRO DE CLIENTE ---")
        self.sistema.registrar_cliente(
            nombre=input("Nombre completo: "),
            documento=input("Número de documento: "),
            email=input("Correo electrónico: "),
            telefono=input("Teléfono (Enter para omitir): ").strip() or None,
        )

    def nueva_reserva(self):
        """Crea el servicio que el cliente elige y registra la reserva."""
        print("\n--- NUEVA RESERVA ---")
        cliente = self.sistema.buscar_cliente(input("Documento del cliente registrado: "))
        if cliente is None:                            # El error ya se mostró y se registró
            return
        print("\n1. Reserva de sala   ($50.000/h; +$15.000/h con proyector)")
        print("2. Alquiler de equipos ($20.000/h por unidad + seguro)")
        print("3. Asesoría especializada ($70.000/h base; máximo 4 horas)")
        servicio = self._crear_servicio_elegido(input("Seleccione el servicio (1-3): ").strip())
        if servicio is None:                           # El servicio no se pudo crear
            return
        horas = float(input("Cantidad de horas: "))    # ValueError si no es un número
        reserva = self.sistema.crear_reserva(cliente, servicio, horas)
        if reserva is not None:                        # Solo si se creó la reserva
            print(f"   Use la opción 3 con el ID {reserva.id} para confirmarla y cobrarla.")

    def _crear_servicio_elegido(self, tipo):
        """Pide los datos del servicio elegido y lo crea."""
        if tipo == "1":                                # Sala
            capacidad = leer_entero("Cantidad de personas: ")
            proyector = input("¿Necesita proyector? (s/n): ").strip().lower() == "s"
            return self.sistema.crear_servicio("sala", nombre=f"Sala para {capacidad}",
                                               tarifa_hora=TARIFAS["sala"], capacidad=capacidad,
                                               con_proyector=proyector)
        if tipo == "2":                                # Equipos
            self.ver_inventario()
            equipo = input("Nombre exacto del equipo: ").strip()
            cantidad = leer_entero("Cantidad de unidades: ")
            return self.sistema.crear_servicio("equipo", nombre=equipo,
                                               tarifa_hora=TARIFAS["equipo"], cantidad=cantidad)
        if tipo == "3":                                # Asesoría
            tema = input("Tema de la asesoría: ").strip()
            nivel = input("Nivel del asesor (junior / senior / experto): ").strip().lower()
            return self.sistema.crear_servicio("asesoria", nombre=tema or "Asesoría",
                                               tarifa_hora=TARIFAS["asesoria"],
                                               especialidad=tema, nivel=nivel)
        print("   ✗ Tipo de servicio no válido.")
        return None

    def procesar_reserva(self):
        """Confirma y cobra una reserva, con descuento opcional."""
        print("\n--- CONFIRMAR Y PROCESAR ---")
        reserva = self.sistema.buscar_reserva(input("ID de la reserva (ej. RES-001 o 1): "))
        if reserva is None:
            return
        texto = input("Descuento en % (Enter si no aplica): ").strip()
        descuento = float(texto) / 100 if texto else None   # Convierte 10 en 0.10
        self.sistema.confirmar_y_procesar(reserva, descuento)

    def cancelar_reserva(self):
        """Cancela una reserva y repone el inventario si era de equipos."""
        print("\n--- CANCELAR RESERVA ---")
        reserva = self.sistema.buscar_reserva(input("ID de la reserva (ej. RES-001 o 1): "))
        if reserva is not None:
            self.sistema.cancelar_reserva(reserva)

    def ver_reservas(self):
        """Muestra todas las reservas."""
        print("\n--- RESERVAS ---")
        if not self.sistema.reservas:                  # Lista vacía
            print("   No hay reservas registradas.")
        for reserva in self.sistema.reservas:
            print("  ", reserva)

    def ver_inventario(self):
        """Muestra las unidades disponibles de cada equipo."""
        print("\n--- INVENTARIO DE EQUIPOS ---")
        for equipo, stock in self.sistema.inventario.items():
            print(f"   - {equipo}: {stock} unidades disponibles")

    def ver_resumen(self):
        """Muestra el resumen general del sistema."""
        print("\n  ", self.sistema.resumen())
