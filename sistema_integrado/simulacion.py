"""
simulacion.py
Simulación automática del sistema Software FJ.

Ejecuta 19 operaciones, válidas e inválidas, para demostrar que el
sistema sigue funcionando aunque ocurran errores. Todos los eventos
quedan registrados en logs/software_fj.log.

Uso:  python simulacion.py   (o la opción 1 del menú de main.py)
"""

from software_fj import SistemaGestion                 # Clase principal del sistema
from software_fj.registro import ARCHIVO_LOG           # Ruta del archivo de logs

LINEA = "=" * 70                                       # Separador visual


def titulo(numero, texto):
    """Imprime el encabezado de cada operación."""
    print(f"\n[{numero:02d}] {texto}")


def operaciones_clientes(sistema):
    """Operaciones 1 a 5: registro de clientes válidos e inválidos."""
    titulo(1, "Registrar cliente válido")
    ana = sistema.registrar_cliente(nombre="ana maría torres", documento="1094567890",
                                    email="ana.torres@correo.com", telefono="3104567890")

    titulo(2, "Registrar cliente con correo inválido")
    sistema.registrar_cliente(nombre="Luis Pérez", documento="88234567", email="luis.correo.com")

    titulo(3, "Registrar cliente sin documento (parámetro faltante)")
    sistema.registrar_cliente(nombre="Carlos Ruiz", documento=None, email="carlos@correo.com")

    titulo(4, "Registrar segundo cliente válido (sin teléfono)")
    pedro = sistema.registrar_cliente(nombre="Pedro Gómez", documento="1098765432",
                                      email="pedro.gomez@empresa.co")

    titulo(5, "Registrar cliente con documento repetido")
    sistema.registrar_cliente(nombre="Ana Duplicada", documento="1094567890", email="otra@correo.com")
    return ana, pedro                                  # Clientes válidos para las reservas


def operaciones_servicios(sistema):
    """Operaciones 6 a 9: creación de servicios válidos e inválidos."""
    titulo(6, "Crear servicios válidos (sala con proyector, equipos y asesoría)")
    sala = sistema.crear_servicio("sala", nombre="Sala Innovación", tarifa_hora=50000,
                                  capacidad=25, con_proyector=True)
    laptops = sistema.crear_servicio("equipo", nombre="Laptop", tarifa_hora=20000, cantidad=3)
    asesoria = sistema.crear_servicio("asesoria", nombre="Arquitectura en la nube",
                                      tarifa_hora=120000, especialidad="Cloud", nivel="senior")

    titulo(7, "Crear servicio con tarifa negativa")
    sistema.crear_servicio("sala", nombre="Sala Básica", tarifa_hora=-1000, capacidad=10)

    titulo(8, "Crear servicio de un tipo inexistente")
    sistema.crear_servicio("transporte", nombre="Van ejecutiva", tarifa_hora=90000)

    titulo(9, "Crear asesoría con nivel no permitido")
    sistema.crear_servicio("asesoria", nombre="Ciberseguridad", tarifa_hora=150000,
                           especialidad="Seguridad", nivel="maestro")
    return sala, laptops, asesoria                     # Servicios válidos para las reservas


def operaciones_reservas(sistema, clientes, servicios):
    """Operaciones 10 a 17: reservas exitosas y fallidas, e inventario."""
    ana, pedro = clientes                              # Desempaqueta los clientes
    sala, laptops, asesoria = servicios                # Desempaqueta los servicios

    titulo(10, "Reserva exitosa: sala por 4 horas con 10 % de descuento")
    sistema.confirmar_y_procesar(sistema.crear_reserva(ana, sala, 4), descuento=0.10)

    titulo(11, "Reserva exitosa: 3 laptops por 24 horas (descuenta del inventario)")
    print(f"   Inventario antes : {sistema.texto_inventario()}")
    sistema.confirmar_y_procesar(sistema.crear_reserva(pedro, laptops, 24))
    print(f"   Inventario después: {sistema.texto_inventario()}")

    titulo(12, "Reserva fallida: asesoría de 6 horas (el máximo es 4)")
    sistema.crear_reserva(ana, asesoria, 6)

    titulo(13, "Reserva fallida: servicio no disponible")
    asesoria.cambiar_disponibilidad(False)             # El asesor queda fuera de servicio
    sistema.crear_reserva(pedro, asesoria, 2)
    asesoria.cambiar_disponibilidad(True)              # Vuelve a estar disponible

    titulo(14, "Cancelar una reserva y luego intentar procesarla")
    reserva = sistema.crear_reserva(pedro, asesoria, 2)
    sistema.cancelar_reserva(reserva)
    sistema.confirmar_y_procesar(reserva)              # No se puede: ya está cancelada

    titulo(15, "Procesar con descuento inválido (error encadenado)")
    pendiente = sistema.crear_reserva(ana, laptops, 8)
    sistema.confirmar_y_procesar(pendiente, descuento=1.5)

    titulo(16, "Reserva fallida: stock insuficiente (5 kits VR, solo hay 3)")
    kits = sistema.crear_servicio("equipo", nombre="Kit VR", tarifa_hora=20000, cantidad=5)
    sistema.crear_reserva(pedro, kits, 2)

    titulo(17, "Cancelar el alquiler de laptops no cobrado (repone el inventario)")
    print(f"   Inventario antes : {sistema.texto_inventario()}")
    sistema.cancelar_reserva(pendiente)
    print(f"   Inventario después: {sistema.texto_inventario()}")


def cotizaciones(sistema, servicios):
    """Operaciones 18 y 19: cálculo inconsistente y método sobrecargado cotizar()."""
    sala, laptops, asesoria = servicios                # Desempaqueta los servicios
    titulo(18, "Cálculo inconsistente: rebaja de $500.000 sobre una sala de $75.000")
    sistema.cotizar_servicio(sala, {"horas": 1, "impuesto": 0, "rebaja": 500000})

    titulo(19, "Cotizaciones con el método sobrecargado cotizar()")
    print(f"   Sala 3 h (int)                  : ${sala.cotizar(3):,.2f}")
    print(f"   Asesoría 1.5 h (float)          : ${asesoria.cotizar(1.5):,.2f}")
    print(f"   Laptops en bloques [2, 4] (list): ${laptops.cotizar([2, 4]):,.2f}")
    print(f"   Sala con descuento (dict)       : ${sala.cotizar({'horas': 2, 'descuento': 0.2}):,.2f}")


def mostrar_resumen(sistema):
    """Muestra el estado final de las reservas y el resumen del sistema."""
    print(f"\n{LINEA}\n RESUMEN\n{LINEA}")
    for reserva in sistema.reservas:                   # Cada reserva con su estado final
        print("  ", reserva)
    print("\n  ", sistema.resumen())
    print(f"   Inventario final: {sistema.texto_inventario()}")
    print(f"\n   El sistema terminó sin interrupciones. Log: {ARCHIVO_LOG}")


def ejecutar_simulacion():
    """Ejecuta la simulación completa de 19 operaciones."""
    print(f"{LINEA}\n SOFTWARE FJ - Simulación automática (19 operaciones)\n{LINEA}")
    sistema = SistemaGestion()                         # Crea el sistema con listas vacías
    clientes = operaciones_clientes(sistema)           # Operaciones 1 a 5
    servicios = operaciones_servicios(sistema)         # Operaciones 6 a 9
    operaciones_reservas(sistema, clientes, servicios)  # Operaciones 10 a 17
    cotizaciones(sistema, servicios)                   # Operaciones 18 y 19
    mostrar_resumen(sistema)                           # Resumen final


if __name__ == "__main__":                             # Solo se ejecuta al correr este archivo
    ejecutar_simulacion()
