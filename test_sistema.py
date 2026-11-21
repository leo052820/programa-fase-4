"""
test_sistema.py
Pruebas unitarias del sistema (se ejecuta con: python -m unittest test_sistema).
"""

import unittest  # Framework de pruebas estandar de Python
from gestor import GestorEmpresa  # Gestor de la logica de negocio
from modelo import (Cliente, Servicio, EntidadBase, ReservaSala,  # Clases del modelo
                    AlquilerEquipo, AsesoriaEspecializada)
from excepciones import (ValidacionError, ParametroFaltanteError,  # Excepciones del sistema
                         ClienteError, StockInsuficienteError, CalculoInconsistenteError,
                         ReservaError, OperacionNoPermitidaError, ServicioNoDisponibleError)


class PruebasModelo(unittest.TestCase):  # Pruebas de las clases del modelo
    """Validaciones de cliente, servicios y calculos."""

    def test_clases_abstractas_no_se_instancian(self):  # Las clases abstractas no se pueden crear
        """EntidadBase y Servicio son abstractas."""
        with self.assertRaises(TypeError):  # Se espera TypeError
            EntidadBase()  # pylint: disable=abstract-class-instantiated
        with self.assertRaises(TypeError):  # Se espera TypeError
            Servicio(2)  # pylint: disable=abstract-class-instantiated

    def test_cliente_valido(self):  # Cliente con datos correctos
        """Normaliza nombre y correo."""
        cliente = Cliente("1001", "laura gomez", "LAURA@correo.com")  # Crea el cliente
        self.assertEqual(cliente.nombre, "Laura Gomez")  # Nombre con mayuscula inicial
        self.assertEqual(cliente.correo, "laura@correo.com")  # Correo en minusculas

    def test_cliente_invalido(self):  # Datos incorrectos
        """Correo, documento y nombre invalidos o faltantes."""
        with self.assertRaises(ValidacionError):  # Correo sin @
            Cliente("1001", "Laura", "laura.correo.com")
        with self.assertRaises(ValidacionError):  # Documento con letras
            Cliente("10A1", "Laura", "laura@correo.com")
        with self.assertRaises(ParametroFaltanteError):  # Nombre vacio
            Cliente("1001", "", "laura@correo.com")

    def test_tarifas_originales(self):  # Las tarifas de Leonardo se conservan
        """Sala con proyector, equipos y asesoria presencial."""
        self.assertEqual(ReservaSala(3, 12, True).calcular_precio(), 195000)  # 3*(50000+15000)
        self.assertEqual(AlquilerEquipo(5, "Laptop", 4).calcular_precio(), 400000)  # 5*4*20000
        self.assertEqual(AsesoriaEspecializada(2, "presencial", "Cloud").calcular_precio(), 190000)  # 2*95000

    def test_limite_asesoria(self):  # Maximo 4 horas
        """Mas de 4 horas o modalidad desconocida generan error."""
        with self.assertRaises(ValidacionError):
            AsesoriaEspecializada(6, "virtual", "Python")
        with self.assertRaises(ValidacionError):
            AsesoriaEspecializada(2, "hibrida", "Python")

    def test_impuesto_descuento_y_rebaja(self):  # Parametros opcionales
        """IVA, descuento y rebaja inconsistente."""
        servicio = AsesoriaEspecializada(1, "virtual", "Python")  # 70000
        self.assertEqual(servicio.calcular_costo(impuesto=0.19), 83300)  # 70000*1.19
        self.assertEqual(servicio.calcular_costo(descuento=0.5), 35000)  # Mitad
        with self.assertRaises(CalculoInconsistenteError):  # Precio negativo
            servicio.calcular_costo(rebaja=100000)
        with self.assertRaises(ValidacionError):  # Descuento fuera de rango
            servicio.calcular_costo(descuento=1.5)

    def test_cotizar_sobrecargado(self):  # Sobrecarga por tipo
        """Entero, lista, diccionario y tipo no soportado."""
        servicio = AsesoriaEspecializada(1, "virtual", "Python")  # 70000 por hora
        self.assertEqual(servicio.cotizar(2), 166600)  # 2h con IVA
        self.assertEqual(servicio.cotizar([1, 1]), 166600)  # Dos bloques de 1h
        self.assertEqual(servicio.cotizar({"impuesto": 0}), 70000)  # Sin impuesto
        with self.assertRaises(ValidacionError):  # Texto no soportado
            servicio.cotizar("dos")


class PruebasGestor(unittest.TestCase):  # Pruebas de la logica de negocio
    """Clientes, stock y estados de reserva."""

    def setUp(self):  # Se ejecuta antes de cada prueba
        self.gestor = GestorEmpresa()  # Gestor limpio
        self.gestor.registrar_cliente("1001", "Laura Gomez", "laura@correo.com")  # Cliente base

    def test_cliente_duplicado_e_inexistente(self):  # Errores de cliente
        """Duplicado al registrar e inexistente al reservar."""
        with self.assertRaises(ClienteError):
            self.gestor.registrar_cliente("1001", "Otra Persona", "otra@correo.com")
        with self.assertRaises(ClienteError):
            self.gestor.crear_reserva("9999", ReservaSala(2, 5, False))

    def test_stock(self):  # Descuento, error y devolucion de stock
        """El stock baja al reservar, se protege y vuelve al cancelar."""
        reserva = self.gestor.crear_reserva("1001", AlquilerEquipo(2, "Laptop", 4))  # Alquila 4
        self.assertEqual(self.gestor.obtener_inventario()["Laptop"], 6)  # Quedan 6
        with self.assertRaises(StockInsuficienteError):  # Pide mas de lo disponible
            self.gestor.crear_reserva("1001", AlquilerEquipo(2, "Kit VR", 5))
        with self.assertRaises(ServicioNoDisponibleError):  # Equipo inexistente
            self.gestor.crear_reserva("1001", AlquilerEquipo(2, "Dron", 1))
        self.gestor.cancelar_reserva(reserva.id_reserva)  # Cancela
        self.assertEqual(self.gestor.obtener_inventario()["Laptop"], 10)  # Stock restaurado

    def test_ciclo_completo(self):  # ACTIVA -> CONFIRMADA -> PROCESADA
        """Confirmar y procesar con IVA."""
        reserva = self.gestor.crear_reserva("1001", ReservaSala(2, 5, False))  # 100000
        self.assertEqual(reserva.estado, "ACTIVA")
        self.gestor.confirmar_reserva(reserva.id_reserva)
        self.assertEqual(self.gestor.procesar_reserva(reserva.id_reserva), 119000)  # Con IVA
        self.assertEqual(reserva.estado, "PROCESADA")

    def test_operaciones_no_permitidas(self):  # Transiciones invalidas
        """Procesar sin confirmar, cancelar procesada, reserva inexistente."""
        reserva = self.gestor.crear_reserva("1001", ReservaSala(2, 5, False))
        with self.assertRaises(OperacionNoPermitidaError):  # Sin confirmar
            self.gestor.procesar_reserva(reserva.id_reserva)
        self.gestor.confirmar_reserva(reserva.id_reserva)
        self.gestor.procesar_reserva(reserva.id_reserva)
        with self.assertRaises(OperacionNoPermitidaError):  # Ya procesada
            self.gestor.cancelar_reserva(reserva.id_reserva)
        with self.assertRaises(ReservaError):  # No existe
            self.gestor.cancelar_reserva(99)

    def test_encadenamiento(self):  # raise ... from
        """Un descuento invalido produce ReservaError con la causa original."""
        reserva = self.gestor.crear_reserva("1001", ReservaSala(2, 5, False))
        self.gestor.confirmar_reserva(reserva.id_reserva)
        with self.assertRaises(ReservaError) as contexto:
            self.gestor.procesar_reserva(reserva.id_reserva, descuento=1.5)
        self.assertIsInstance(contexto.exception.__cause__, ValidacionError)  # Causa conservada
        self.assertEqual(reserva.estado, "CONFIRMADA")  # El estado no cambio


if __name__ == "__main__":  # Permite ejecutar este archivo directamente
    unittest.main()  # Corre las pruebas
