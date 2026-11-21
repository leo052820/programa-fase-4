# programa fase 4
fase 4 - componente practico - practicas simuladas


# Sistema de Gestion de Servicios Tecnologicos

Aplicacion modular en Python para administrar clientes, reservas, calculo automatico de tarifas e inventario de una empresa de servicios tecnologicos.

# Servicios Implementados
1. **Reserva de Salas:** Cobro por hora ($50,000/h) + adicional opcional de proyector ($15,000/h) e indicacion de aforo.
2. **Alquiler de Equipos:** Cobro por hora y unidad ($20,000/h) con control de stock en tiempo real y reposicion automatica al cancelar.
3. **Asesorias Especializadas:** Modalidad virtual ($70,000/h) o presencial ($95,000/h) con restriccion estricta de maximo 4 horas.

# Estructura de Archivos
gestor.py: Logica de negocio, almacenamiento en memoria y control de inventario.
sistema.py: Menus interactivos por consola.
simulacion.py: Script de pruebas automatizadas y carga de datos iniciales.
main.py: Archivo principal de ejecucion.modelo.py: Clases del dominio (entidad abstracta, cliente, servicios y reserva).
excepciones.py: Excepciones personalizadas del sistema.
registro.py: Configuracion del archivo de logs (sistema.log).
test_sistema.py: Pruebas unitarias.

# Complemento segun el Anexo 3
Sobre la version inicial se agrego, sin cambiar las tarifas, el inventario ni el menu original:
- **Clase abstracta general** `EntidadBase`, de la que heredan `Cliente`, `Servicio` y `Reserva`.
- **Cliente** con atributos privados, propiedades y validacion de documento, nombre y correo.
- **Servicios** con metodos sobrescritos: `calcular_precio`, `validar_parametros` y `obtener_detalle`.
- **Metodos sobrecargados**: `calcular_costo(impuesto, descuento, rebaja)` con parametros opcionales y `cotizar(...)` que acepta un entero (horas), una lista (bloques) o un diccionario (opciones).
- **Reserva** con estados ACTIVA, CONFIRMADA, PROCESADA y CANCELADA (`confirmar`, `procesar`, `cancelar`).
- **Excepciones personalizadas** con codigo (FJ-100 a FJ-410), bloques try/except, try/except/else, try/except/finally y encadenamiento (`raise ... from`).
- **Archivo de logs** con los eventos y errores en `sistema.log`.
- **Simulacion** de 18 operaciones validas e invalidas; el sistema sigue funcionando aunque ocurran errores.

# Como ejecutar
```
python main.py
```
Opcion 1: simulacion automatica. Opcion 2: menu interactivo.

Pruebas unitarias:
```
python -m unittest test_sistema
```

# Integrantes
Alejandro Arias Lopez, Jose Leonardo Lopez Rangel, Jimena Jacome Contreras.
