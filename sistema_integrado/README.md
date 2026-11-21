# programa fase 4
Fase 4 - Componente práctico - Prácticas simuladas · Curso **Programación (213023)** · UNAD

# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Aplicación orientada a objetos en Python, **sin base de datos**, que gestiona clientes, servicios
(reserva de salas, alquiler de equipos y asesorías especializadas), reservas e inventario de equipos,
con **manejo avanzado de excepciones** y registro de eventos en un archivo de logs.

> La versión inicial del proyecto (archivos `main.py`, `modelo.py`, `gestor.py`, `sistema.py` y
> `simulacion.py` en la raíz del repositorio) se conserva sin cambios. Esta carpeta contiene la
> versión integrada que cumple todos los requisitos del Anexo 3.

## Integrantes y aportes

| Integrante | Aporte |
|---|---|
| José Leonardo López Rangel | Versión inicial: modelo de servicios con tarifas, inventario de equipos con stock, menú interactivo por consola y simulación inicial |
| Jimena Jácome Contreras | Clase abstracta de entidades, Cliente con encapsulación y validaciones, excepciones personalizadas, archivo de logs, métodos sobrecargados, ciclo de estados de la reserva, simulación de 19 operaciones, pruebas unitarias e integración del menú y el inventario |

## Requisitos

- Python 3.10 o superior (solo usa la biblioteca estándar; no requiere instalar paquetes).

## Ejecución

Desde la carpeta `sistema_integrado`:

```bash
python main.py                                  # Menú de inicio: 1) simulación  2) menú interactivo
python simulacion.py                            # Ejecuta directamente la simulación de 19 operaciones
python -m unittest discover -s tests -v         # Ejecuta las 16 pruebas unitarias
```

Los eventos y errores quedan registrados en `logs/software_fj.log`.

## Calidad del código

- `pylint`: 10.00/10 (configuración en `.pylintrc`)
- `pycodestyle` y `pyflakes`: sin advertencias
- Cada línea de código está documentada con un comentario.

## Estructura del proyecto

```
sistema_integrado/
├── main.py                  # Menú de inicio (simulación o menú interactivo)
├── simulacion.py            # Simulación automática de 19 operaciones
├── software_fj/
│   ├── __init__.py          # Exporta las clases principales
│   ├── excepciones.py       # Excepciones personalizadas (jerarquía SoftwareFJError)
│   ├── registro.py          # Configuración del archivo de logs
│   ├── entidad.py           # Clase abstracta EntidadBase
│   ├── cliente.py           # Clase Cliente con encapsulación y validaciones
│   ├── servicios.py         # Clase abstracta Servicio y 3 servicios especializados
│   ├── reserva.py           # Clase Reserva y estados (confirmar, cancelar, procesar)
│   ├── sistema.py           # SistemaGestion: listas internas, inventario y operaciones protegidas
│   └── interfaz.py          # Menú interactivo por consola
└── tests/
    └── test_sistema.py      # Pruebas unitarias
```

## Servicios implementados

1. **Reserva de salas:** tarifa por hora, recargo del 20 % para salas de más de 20 personas y proyector opcional ($15.000/h).
2. **Alquiler de equipos:** tarifa por hora y unidad, seguro por equipo y control de stock (Laptop, Tablet, Camara, Kit VR); el stock se repone al cancelar.
3. **Asesorías especializadas:** tarifa por hora según el nivel del asesor (junior, senior, experto), máximo 4 horas.

## Cómo se cumple cada requisito del Anexo 3

| Requisito | Dónde está |
|---|---|
| Clase abstracta para entidades generales | `EntidadBase` (`entidad.py`) con `describir()` y `validar()` abstractos |
| Cliente con validaciones y encapsulación | `Cliente`: atributos privados y propiedades que validan nombre, documento, correo y teléfono |
| Clase abstracta Servicio + 3 servicios | `Servicio` → `ReservaSala`, `AlquilerEquipo`, `Asesoria` |
| Polimorfismo y métodos sobrescritos | Cada servicio sobrescribe `costo_base()`, `validar_parametros()` y `describir()` |
| Métodos sobrecargados | `calcular_costo(horas, impuesto=None, descuento=None, rebaja=None)` y `cotizar()` con `@singledispatchmethod` (acepta `int`, `float`, `list` o `dict`) |
| Clase Reserva | `Reserva`: cliente, servicio, duración y estado; `confirmar()`, `cancelar()`, `procesar()` |
| Excepciones personalizadas | `ValidacionError`, `ParametroFaltanteError`, `ClienteInvalidoError`, `ServicioNoDisponibleError`, `StockInsuficienteError`, `CalculoInconsistenteError`, `ReservaError`, `OperacionNoPermitidaError` |
| `try/except` | `Reserva.procesar()` y todas las operaciones de `sistema.py` |
| `try/except/else` | `registrar_cliente()`, `crear_servicio()`, `crear_reserva()`, `cotizar_servicio()` |
| `try/except/finally` | `cancelar_reserva()` e `interfaz.ejecutar()` |
| `try/except/else/finally` | `Reserva.procesar()` y `confirmar_y_procesar()` |
| Encadenamiento de excepciones | `raise ReservaError(...) from error` en `Reserva.procesar()` y causas `KeyError`/`TypeError` en `sistema.py` |
| Archivo de logs | `registro.py` → `logs/software_fj.log` |
| Listas internas, sin base de datos | `SistemaGestion.clientes`, `.servicios`, `.reservas` e `.inventario` |
| Errores contemplados | Datos inválidos, parámetros faltantes, operaciones no permitidas, reservas incorrectas, servicios no disponibles, stock insuficiente y cálculos inconsistentes |
| Al menos 10 operaciones simuladas | `simulacion.py` ejecuta 19 operaciones (7 exitosas y 12 con errores controlados) |

## Operaciones simuladas

1. Registrar cliente válido
2. Cliente con correo inválido
3. Cliente sin documento
4. Segundo cliente válido
5. Cliente con documento repetido
6. Crear tres servicios válidos (sala con proyector, laptops y asesoría)
7. Servicio con tarifa negativa
8. Servicio de tipo inexistente (excepción encadenada con `KeyError`)
9. Asesoría con nivel no permitido
10. Reserva de sala exitosa con descuento
11. Alquiler de laptops exitoso (descuenta del inventario)
12. Asesoría de más de 4 horas
13. Reserva de un servicio no disponible
14. Cancelar y luego intentar procesar una reserva
15. Procesar con descuento inválido (excepción encadenada)
16. Stock insuficiente de equipos
17. Cancelar un alquiler (repone el inventario)
18. Cálculo inconsistente: rebaja mayor que el costo
19. Cotizaciones con el método sobrecargado `cotizar()`
