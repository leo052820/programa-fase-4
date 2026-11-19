from gestor import GestorEmpresa  # Importa el gestor de logica de negocio
from modelo import ReservaSala, AlquilerEquipo, AsesoriaEspecializada  # Importa las clases de servicios

class SistemaInterfaz:  # Clase responsable de la interaccion por consola con el usuario
    def __init__(self, gestor: GestorEmpresa):  # Constructor que recibe una instancia de GestorEmpresa
        self.gestor = gestor  # Guarda la referencia al gestor para operar sobre los datos

    def iniciar(self):  # Inicia el ciclo principal del menu interactivo
        while True:  # Bucle infinito hasta que el usuario elija salir
            print("\n" + "=" * 45)  # Imprime linea separadora superior
            print("   SISTEMA DE GESTION DE SERVICIOS TECH")  # Imprime titulo del sistema
            print("=" * 45)  # Imprime linea separadora inferior
            print("1. Registrar cliente")  # Opcion 1 del menu
            print("2. Realizar nueva reserva")  # Opcion 2 del menu
            print("3. Ver historial de reservas")  # Opcion 3 del menu
            print("4. Cancelar reserva")  # Opcion 4 del menu
            print("5. Ver inventario de equipos disponibles")  # Opcion 5 del menu
            print("6. Salir")  # Opcion 6 del menu
            
            opcion = input("\nSeleccione una opcion (1-6): ").strip()  # Lee la opcion ingresada y limpia espacios

            try:  # Bloque para capturar errores controlados o inesperados durante la ejecucion
                if opcion == "1":  # Si el usuario eligio registrar cliente
                    self._menu_registrar_cliente()  # Ejecuta el flujo de registro de cliente
                elif opcion == "2":  # Si el usuario eligio crear una reserva
                    self._menu_nueva_reserva()  # Ejecuta el flujo de creacion de reserva
                elif opcion == "3":  # Si el usuario eligio ver reservas
                    self._menu_listar_reservas()  # Muestra el historial de reservas
                elif opcion == "4":  # Si el usuario eligio cancelar una reserva
                    self._menu_cancelar_reserva()  # Ejecuta el flujo de cancelacion de reserva
                elif opcion == "5":  # Si el usuario eligio ver inventario
                    self._menu_inventario()  # Muestra el stock disponible de equipos
                elif opcion == "6":  # Si el usuario eligio salir del programa
                    print("Saliendo del sistema. Hasta pronto!")  # Mensaje de despedida
                    break  # Rompe el bucle while y finaliza el programa
                else:  # Si se ingresa cualquier otro texto o numero fuera de rango
                    print("Opcion no valida. Intente nuevamente.")  # Informa que la opcion no existe
            except ValueError as e:  # Captura errores de validacion de datos o reglas de negocio
                print(f"\n[ERROR]: {e}")  # Muestra el mensaje de error amigable en consola
            except Exception as e:  # Captura cualquier otro error no previsto (ej. escribir letras donde va numero)
                print(f"\n[ERROR INESPERADO]: {e}")  # Muestra detalle del error inesperado

    def _menu_registrar_cliente(self):  # Submenu para registrar un cliente
        print("\n--- REGISTRO DE CLIENTE ---")  # Encabezado de seccion
        doc = input("Numero de documento: ").strip()  # Solicita documento del cliente
        nombre = input("Nombre completo: ").strip()  # Solicita nombre del cliente
        correo = input("Correo electronico: ").strip()  # Solicita correo del cliente
        if not doc or not nombre:  # Verifica que documento y nombre no esten vacios
            raise ValueError("El documento y el nombre son obligatorios.")  # Lanza error si faltan datos clave
        cliente = self.gestor.registrar_cliente(doc, nombre, correo)  # Registra al cliente en el gestor
        print(f"Cliente registrado con exito: {cliente}")  # Confirma el registro exitoso

    def _menu_nueva_reserva(self):  # Submenu para seleccionar servicio y crear una reserva
        print("\n--- NUEVA RESERVA ---")  # Encabezado de seccion
        doc = input("Documento del cliente registrado: ").strip()  # Pide documento para asociar la reserva
        self.gestor.buscar_cliente(doc)  # Verifica que el cliente exista antes de pedir datos del servicio

        print("\nServicios disponibles:")  # Muestra catalogo de servicios y tarifas
        print("1. Reserva de Salas ($50,000/h + $15,000/h proyector)")  # Info servicio 1
        print("2. Alquiler de Equipos ($20,000/h por unidad)")  # Info servicio 2
        print("3. Asesorias Especializadas ($70,000/h Virtual | $95,000/h Presencial - Max 4h)")  # Info servicio 3
        tipo = input("Seleccione el servicio (1-3): ").strip()  # Lee el tipo de servicio seleccionado

        if tipo == "1":  # Flujo para Reserva de Sala
            horas = int(input("Cantidad de horas: "))  # Solicita duracion en horas
            personas = int(input("Cantidad de personas: "))  # Solicita numero de asistentes
            proy = input("Necesita proyector? (s/n): ").strip().lower() == "s"  # Convierte respuesta 's' en True
            servicio = ReservaSala(horas, personas, proy)  # Crea la instancia de ReservaSala

        elif tipo == "2":  # Flujo para Alquiler de Equipo
            self._menu_inventario()  # Muestra los equipos y cantidades disponibles actualmente
            equipo = input("Nombre exacto del equipo a alquilar: ").strip()  # Solicita nombre del equipo
            if equipo not in self.gestor.obtener_inventario():  # Comprueba si el equipo existe en el inventario
                raise ValueError("El equipo ingresado no existe en el catalogo.")  # Lanza error si no existe
            cantidad = int(input("Cantidad de unidades: "))  # Solicita numero de unidades a alquilar
            horas = int(input("Cantidad de horas: "))  # Solicita duracion del alquiler en horas
            servicio = AlquilerEquipo(horas, equipo, cantidad)  # Crea la instancia de AlquilerEquipo

        elif tipo == "3":  # Flujo para Asesoria Especializada
            modalidad = input("Modalidad (virtual / presencial): ").strip()  # Solicita modalidad de asesoria
            tema = input("Tema de la asesoria: ").strip()  # Solicita el tema a tratar
            horas = int(input("Cantidad de horas (maximo 4): "))  # Solicita horas (validara max 4 en el modelo)
            servicio = AsesoriaEspecializada(horas, modalidad, tema)  # Crea la instancia de AsesoriaEspecializada
        else:  # Si el tipo de servicio no esta entre 1 y 3
            raise ValueError("Tipo de servicio no valido.")  # Lanza error por seleccion invalida

        reserva = self.gestor.crear_reserva(doc, servicio)  # Crea la reserva en el gestor y descuenta stock si aplica
        print("\nReserva creada exitosamente!")  # Mensaje de confirmacion
        print(reserva)  # Imprime los detalles y el precio total calculado de la reserva

    def _menu_listar_reservas(self):  # Submenu para consultar todas las reservas
        print("\n--- LISTADO DE RESERVAS ---")  # Encabezado de seccion
        reservas = self.gestor.listar_reservas()  # Obtiene la lista de reservas del gestor
        if not reservas:  # Si no hay ninguna reserva registrada
            print("No hay reservas registradas aun.")  # Informa que la lista esta vacia
            return  # Sale del metodo anticipadamente
        for r in reservas:  # Itera sobre cada reserva registrada
            print(r)  # Imprime la informacion de la reserva

    def _menu_cancelar_reserva(self):  # Submenu para cancelar una reserva por ID
        print("\n--- CANCELAR RESERVA ---")  # Encabezado de seccion
        id_res = int(input("Ingrese el ID de la reserva a cancelar: "))  # Solicita el ID numerico de la reserva
        reserva = self.gestor.cancelar_reserva(id_res)  # Cancela la reserva y repone stock si era equipo
        print(f"Reserva #{reserva.id_reserva} cancelada correctamente. Stock actualizado si aplica.")  # Confirma cancelacion

    def _menu_inventario(self):  # Submenu para mostrar el inventario actual de equipos
        print("\n--- INVENTARIO DE EQUIPOS ---")  # Encabezado de seccion
        for equipo, stock in self.gestor.obtener_inventario().items():  # Recorre cada equipo y su cantidad disponible
            print(f"- {equipo}: {stock} unidades disponibles")  # Muestra el equipo y su stock actual