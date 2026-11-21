"""
simulacion.py
Simulacion automatica con operaciones validas e invalidas.

Version inicial: Jose Leonardo Lopez Rangel y Alejandro Arias Lopez (pasos 1 a 6).
Complemento: Jimena Jacome Contreras (operaciones 7 a 18: errores de
validacion, stock, estados, calculo inconsistente, encadenamiento y
metodos sobrecargados). El sistema sigue funcionando aunque ocurran errores.
"""
from gestor import GestorEmpresa  # Importa el gestor principal del sistema
from modelo import ReservaSala, AlquilerEquipo, AsesoriaEspecializada  # Importa las clases de servicios
from excepciones import SoftwareFJError  # Excepcion base del sistema (complemento)


def cargar_datos_iniciales(gestor: GestorEmpresa):  # Funcion auxiliar para cargar clientes de prueba
    """Carga clientes base para facilitar pruebas inmediatas."""  # Docstring que explica el proposito de la funcion
    gestor.registrar_cliente("1001", "Laura Gomez", "laura@correo.com")  # Registra cliente de prueba #1
    gestor.registrar_cliente("1002", "Carlos Ruiz", "carlos@correo.com")  # Registra cliente de prueba #2


def intentar(gestor, numero, descripcion, operacion):  # Ejecuta una operacion sin que un error detenga la simulacion
    """Ejecuta la operacion e informa si fue exitosa o si genero un error controlado."""
    print(f"\n{numero}. {descripcion}")  # Muestra el numero y la descripcion de la operacion
    try:  # Intenta ejecutar la operacion
        resultado = operacion()  # Ejecuta la funcion recibida
    except SoftwareFJError as error:  # Error propio del sistema
        print(f"   [Error controlado] {error}")  # Muestra el error con su codigo
        if not getattr(error, "registrado", False):  # Si el error ocurrio fuera del gestor...
            gestor.registrar_error(descripcion, error)  # ...tambien se registra en el log
        if error.__cause__:  # Si fue encadenado...
            print(f"   Causa original: {error.__cause__}")  # ...muestra la causa
        return None  # Indica que la operacion no tuvo resultado
    else:  # Solo si no hubo error
        print(f"   [OK] {resultado}")  # Muestra el resultado
        return resultado  # Retorna el resultado para usarlo despues
    finally:  # Siempre se ejecuta
        print("   " + "-" * 40)  # Separador visual entre operaciones


def ejecutar_simulacion_completa():  # Ejecuta una prueba automatica de todas las funcionalidades
    """Ejecuta los pasos originales (1 a 6) y las operaciones agregadas (7 a 18)."""
    print("==================================================")  # Separador visual superior
    print("   INICIANDO SIMULACION AUTOMATICA DEL SISTEMA")  # Titulo de la simulacion
    print("==================================================\n")  # Separador visual inferior

    gestor = GestorEmpresa()  # Crea una nueva instancia limpia del gestor
    cargar_datos_iniciales(gestor)  # Carga los clientes iniciales de prueba
    print("1. Clientes de prueba registrados (IDs: 1001 y 1002).")  # Informa que los clientes ya estan listos

    r1 = gestor.crear_reserva("1001", ReservaSala(horas=3, num_personas=12, con_proyector=True))  # Reserva sala 3h con proyector
    print(f"2. Creada -> {r1}")  # Muestra resultado y precio de la reserva de sala

    print(f"   Stock Laptops antes: {gestor.obtener_inventario()['Laptop']}")  # Muestra stock de laptops antes de alquilar
    r2 = gestor.crear_reserva("1002", AlquilerEquipo(horas=5, nombre_equipo="Laptop", cantidad=4))  # Alquila 4 laptops por 5h
    print(f"3. Creada -> {r2}")  # Muestra resultado y precio del alquiler de equipos
    print(f"   Stock Laptops despues: {gestor.obtener_inventario()['Laptop']}")  # Muestra stock de laptops tras descontar 4

    r3 = gestor.crear_reserva("1001", AsesoriaEspecializada(horas=2, modalidad="presencial", tema="Arquitectura Cloud"))  # Reserva asesoria presencial 2h
    print(f"4. Creada -> {r3}")  # Muestra resultado y precio de la asesoria

    print("\n5. Probando restriccion de >4 horas en asesoria:")  # Anuncia prueba de limite maximo de horas
    try:  # Intenta crear una asesoria invalida de 6 horas
        gestor.crear_reserva("1002", AsesoriaEspecializada(horas=6, modalidad="virtual", tema="Python"))  # Debe lanzar ValueError
    except ValueError as e:  # Captura el error esperado por superar 4 horas
        print(f"   [Bloqueo exitoso]: {e}")  # Confirma que la regla de negocio funciono correctamente
        gestor.registrar_error("Asesoria de 6 horas", e)  # Complemento: deja el error en el sistema.log

    print("\n6. Cancelando Reserva #2 (Alquiler de Laptops)...")  # Anuncia la cancelacion de la reserva de equipos
    gestor.cancelar_reserva(r2.id_reserva)  # Cancela la reserva #2 y devuelve las 4 laptops al inventario
    print(f"   Estado actualizado -> {r2}")  # Muestra que la reserva ahora figura como CANCELADA
    print(f"   Stock Laptops restaurado: {gestor.obtener_inventario()['Laptop']}")  # Confirma que las 4 laptops volvieron al stock

    # ----- Operaciones agregadas (Jimena) -----
    intentar(gestor, 7, "Registrar cliente con correo invalido",  # Operacion 7 (invalida)
             lambda: gestor.registrar_cliente("1003", "Ana Torres", "ana-correo.com"))  # Correo sin @
    intentar(gestor, 8, "Registrar cliente con documento duplicado (1001)",  # Operacion 8 (invalida)
             lambda: gestor.registrar_cliente("1001", "Laura Gomez", "otra@correo.com"))  # Documento ya registrado
    intentar(gestor, 9, "Registrar cliente valido (1003 Ana Torres)",  # Operacion 9 (valida)
             lambda: gestor.registrar_cliente("1003", "Ana Torres", "ana@correo.com"))  # Registra a Ana Torres
    intentar(gestor, 10, "Reservar para un cliente que no existe (9999)",  # Operacion 10 (invalida)
             lambda: gestor.crear_reserva("9999", ReservaSala(2, 5, False)))  # El cliente 9999 no existe
    intentar(gestor, 11, "Alquilar 5 Kit VR (solo hay 3)",  # Operacion 11 (invalida)
             lambda: gestor.crear_reserva("1003", AlquilerEquipo(4, "Kit VR", 5)))  # Pide mas Kit VR de los disponibles
    intentar(gestor, 12, "Confirmar y procesar la reserva #1 con 10 % de descuento",  # Operacion 12 (valida)
             lambda: (gestor.confirmar_reserva(r1.id_reserva),  # Primero confirma la reserva #1
                      f"Cobrado: ${gestor.procesar_reserva(r1.id_reserva, descuento=0.10):,.0f}")[1])  # Luego la cobra con 10 % de descuento
    intentar(gestor, 13, "Procesar la reserva #2, que esta CANCELADA",  # Operacion 13 (invalida)
             lambda: gestor.procesar_reserva(r2.id_reserva))  # No se puede cobrar una reserva cancelada
    r4 = intentar(gestor, 14, "Asesoria virtual 3h en Ciberseguridad para Ana",  # Operacion 14 (valida)
                  lambda: gestor.crear_reserva("1003", AsesoriaEspecializada(3, "virtual", "Ciberseguridad")))  # Crea la asesoria virtual de 3 horas
    intentar(gestor, 15, "Confirmar y procesar la reserva #4 con descuento de 150 % (error encadenado)",  # Operacion 15 (invalida)
             lambda: (gestor.confirmar_reserva(r4.id_reserva),  # Confirma la reserva #4
                      gestor.procesar_reserva(r4.id_reserva, descuento=1.5))[1])  # Descuento invalido: genera un error encadenado
    intentar(gestor, 16, "Calcular precio con rebaja mayor al valor (calculo inconsistente)",  # Operacion 16 (invalida)
             lambda: r4.servicio.calcular_costo(rebaja=500000))  # La rebaja deja el precio en negativo
    intentar(gestor, 17, "Cotizaciones sobrecargadas: entero, lista y diccionario",  # Operacion 17 (valida)
             lambda: (f"4h: ${r4.servicio.cotizar(4):,.0f} | bloques [1,2]: ${r4.servicio.cotizar([1, 2]):,.0f} | "  # Cotiza 4 horas y bloques de horas
                      f"5 % desc.: ${r4.servicio.cotizar({'descuento': 0.05}):,.0f}"))  # Cotiza con un diccionario de opciones
    intentar(gestor, 18, "Cancelar la reserva #1, que ya fue PROCESADA",  # Operacion 18 (invalida)
             lambda: gestor.cancelar_reserva(r1.id_reserva))  # No se cancela una reserva ya cobrada

    print("\nRESERVAS REGISTRADAS:")  # Encabezado del listado final
    for reserva in gestor.listar_reservas():  # Recorre todas las reservas
        print(f"   {reserva}")  # Muestra cada reserva con su estado
    print("\n==================================================")  # Separador final superior
    print("   SIMULACION FINALIZADA EXITOSAMENTE")  # Mensaje de cierre de la simulacion
    print(f"   {gestor.resumen()}")  # Muestra el resumen general (complemento)
    print("   Detalle de eventos y errores en sistema.log")  # Indica donde quedo el log (complemento)
    print("==================================================")  # Separador final inferior


if __name__ == "__main__":  # Verifica que el archivo se este ejecutando directamente
    ejecutar_simulacion_completa()  # Llama a la funcion principal de simulacion
