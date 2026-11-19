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
main.py: Archivo principal de ejecucion.