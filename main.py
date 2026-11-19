from gestor import GestorEmpresa  # Importa la clase que gestiona clientes, inventario y reservas
from sistema import SistemaInterfaz  # Importa la interfaz interactiva de consola
from simulacion import cargar_datos_iniciales  # Importa la funcion para cargar clientes base

def main():  # Funcion principal de arranque de la aplicacion
    gestor = GestorEmpresa()  # Instancia el gestor de la empresa
    
    cargar_datos_iniciales(gestor)  # Precarga clientes de ejemplo (IDs 1001 y 1002) para probar rapido
    
    app = SistemaInterfaz(gestor)  # Crea la interfaz de usuario conectada al gestor
    app.iniciar()  # Arranca el menu interactivo en consola

if __name__ == "__main__":  # Garantiza que main() solo corra al ejecutar main.py directamente
    main()  # Ejecuta la funcion principal