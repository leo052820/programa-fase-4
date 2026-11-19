from gestor import GestorEmpresa  # Importa el gestor principal del sistema
from modelo import ReservaSala, AlquilerEquipo, AsesoriaEspecializada  # Importa las clases de servicios

def cargar_datos_iniciales(gestor: GestorEmpresa):  # Funcion auxiliar para cargar clientes de prueba
    """Carga clientes base para facilitar pruebas inmediatas."""  # Docstring que explica el proposito de la funcion
    gestor.registrar_cliente("1001", "Laura Gomez", "laura@correo.com")  # Registra cliente de prueba #1
    gestor.registrar_cliente("1002", "Carlos Ruiz", "carlos@correo.com")  # Registra cliente de prueba #2

def ejecutar_simulacion_completa():  # Ejecuta una prueba automatica de todas las funcionalidades
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

    print("\n6. Cancelando Reserva #2 (Alquiler de Laptops)...")  # Anuncia la cancelacion de la reserva de equipos
    gestor.cancelar_reserva(r2.id_reserva)  # Cancela la reserva #2 y devuelve las 4 laptops al inventario
    print(f"   Estado actualizado -> {r2}")  # Muestra que la reserva ahora figura como CANCELADA
    print(f"   Stock Laptops restaurado: {gestor.obtener_inventario()['Laptop']}")  # Confirma que las 4 laptops volvieron al stock

    print("\n==================================================")  # Separador final superior
    print("   SIMULACION FINALIZADA EXITOSAMENTE")  # Mensaje de cierre de la simulacion
    print("==================================================")  # Separador final inferior

if __name__ == "__main__":  # Verifica que el archivo se este ejecutando directamente
    ejecutar_simulacion_completa()  # Llama a la funcion principal de simulacion