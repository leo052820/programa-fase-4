"""
main.py
Punto de entrada del sistema Software FJ.

Permite elegir entre:
  1. La simulación automática de 19 operaciones (válidas e inválidas).
  2. El menú interactivo por consola.

Uso:  python main.py
"""

import sys                                             # Acceso a la salida estándar
from simulacion import ejecutar_simulacion             # Simulación automática
from software_fj.interfaz import SistemaInterfaz       # Menú interactivo


def configurar_consola():
    """Asegura que la consola muestre tildes y los símbolos ✓ ✗ (necesario en Windows)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")       # Cambia la codificación de salida a UTF-8
    except (AttributeError, ValueError):               # Si no se puede cambiar, se continúa igual
        pass


def main():
    """Muestra el menú de inicio y ejecuta el modo elegido."""
    configurar_consola()
    print("=" * 55)
    print(" SOFTWARE FJ - Gestión de Clientes, Servicios y Reservas")
    print("=" * 55)
    print("1. Ejecutar la simulación automática (19 operaciones)")
    print("2. Abrir el menú interactivo")
    print("3. Salir")
    opcion = input("\nSeleccione una opción (1-3): ").strip()
    if opcion == "1":
        ejecutar_simulacion()
    elif opcion == "2":
        SistemaInterfaz().iniciar()
    else:
        print("Hasta pronto.")


if __name__ == "__main__":                             # Solo se ejecuta al correr este archivo
    main()
