#Trabajo presentado por: Alejandro Arias Lopez, Jose Leonardo Lopez, jimena jacome
"""Punto de entrada: permite elegir entre la simulacion automatica y el menu interactivo."""
import sys  # Acceso a la configuracion de la consola (complemento)
from gestor import GestorEmpresa  # Importa la clase que gestiona clientes, inventario y reservas
from sistema import SistemaInterfaz  # Importa la interfaz interactiva de consola
from simulacion import cargar_datos_iniciales  # Importa la funcion para cargar clientes base
from simulacion import ejecutar_simulacion_completa  # Importa la simulacion automatica (complemento)

if hasattr(sys.stdout, "reconfigure"):  # Si la consola permite reconfigurarse...
    sys.stdout.reconfigure(encoding="utf-8")  # ...usa UTF-8 para evitar errores de caracteres en Windows


def main():  # Funcion principal de arranque de la aplicacion
    """Inicia el menu interactivo con los clientes de prueba cargados."""
    gestor = GestorEmpresa()  # Instancia el gestor de la empresa

    cargar_datos_iniciales(gestor)  # Precarga clientes de ejemplo (IDs 1001 y 1002) para probar rapido

    app = SistemaInterfaz(gestor)  # Crea la interfaz de usuario conectada al gestor
    app.iniciar()  # Arranca el menu interactivo en consola


def seleccionar_modo():  # Complemento: permite elegir como ejecutar el programa
    """Pregunta si se ejecuta la simulacion automatica o el menu interactivo."""
    print("1. Ejecutar simulacion automatica (operaciones validas e invalidas)")  # Opcion 1
    print("2. Usar el menu interactivo")  # Opcion 2
    opcion = input("Seleccione una opcion (1-2): ").strip()  # Lee la opcion
    if opcion == "1":  # Si elige la simulacion
        ejecutar_simulacion_completa()  # Ejecuta la simulacion completa
    else:  # Cualquier otra respuesta abre el menu
        main()  # Ejecuta la funcion principal


if __name__ == "__main__":  # Garantiza que el programa solo corra al ejecutar main.py directamente
    seleccionar_modo()  # Pregunta el modo y ejecuta la opcion elegida
