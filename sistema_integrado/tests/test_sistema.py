"""
test_sistema.py
Pruebas unitarias del sistema Software FJ.
Uso:  python -m unittest discover -s tests -v
"""

import unittest                                        # Framework de pruebas incluido en Python
from software_fj import Cliente, ReservaSala, AlquilerEquipo, Asesoria, Reserva, EstadoReserva, SistemaGestion
from software_fj.entidad import EntidadBase            # Para comprobar que es abstracta
from software_fj.servicios import Servicio
from software_fj.excepciones import (ValidacionError, ParametroFaltanteError, ServicioNoDisponibleError,
                                     OperacionNoPermitidaError, ReservaError, CalculoInconsistenteError)


class PruebasCliente(unittest.TestCase):
    """Pruebas de la clase Cliente."""

    def test_cliente_valido(self):
        """Un cliente con datos correctos se crea bien."""
        c = Cliente("ana torres", "1094567890", "Ana@Correo.com", "3104567890")
        self.assertEqual(c.nombre, "Ana Torres")       # El nombre se normaliza
        self.assertEqual(c.email, "ana@correo.com")    # El correo se pasa a minúsculas

    def test_email_invalido(self):
        """Un correo sin @ se rechaza."""
        with self.assertRaises(ValidacionError):
            Cliente("Luis Pérez", "88234567", "luis.correo.com")

    def test_documento_faltante(self):
        """Sin documento se lanza ParametroFaltanteError."""
        with self.assertRaises(ParametroFaltanteError):
            Cliente("Carlos Ruiz", None, "carlos@correo.com")

    def test_encapsulacion(self):
        """Un cambio inválido por propiedad se rechaza."""
        c = Cliente("Ana Torres", "1094567890", "ana@correo.com")
        with self.assertRaises(ValidacionError):
            c.telefono = "abc"


class PruebasServicios(unittest.TestCase):
    """Pruebas de los servicios, el polimorfismo y la sobrecarga."""

    def test_clases_abstractas(self):
        """Las clases abstractas no se pueden instanciar."""
        with self.assertRaises(TypeError):
            EntidadBase("X")  # pylint: disable=abstract-class-instantiated
        with self.assertRaises(TypeError):
            Servicio("Genérico", 1000)  # pylint: disable=abstract-class-instantiated

    def test_polimorfismo_costos(self):
        """Cada servicio calcula su costo a su manera."""
        sala = ReservaSala("Sala", 50000, capacidad=25)        # 50.000 x 2 h x 1.2 = 120.000
        equipo = AlquilerEquipo("PC", 8000, cantidad=2)        # 8.000 x 2 h x 2 + 30.000 = 62.000
        asesoria = Asesoria("Nube", 100000, "Cloud", "experto")   # 100.000 x 2 h x 2 = 400.000
        self.assertEqual(sala.calcular_costo(2), 120000)
        self.assertEqual(equipo.calcular_costo(2), 62000)
        self.assertEqual(asesoria.calcular_costo(2), 400000)

    def test_sobrecarga_calcular_costo(self):
        """Variantes con impuesto y descuento."""
        sala = ReservaSala("Sala", 10000, capacidad=10)
        self.assertEqual(sala.calcular_costo(2), 20000)
        self.assertEqual(sala.calcular_costo(2, impuesto=0.19), 23800)
        self.assertEqual(sala.calcular_costo(2, descuento=0.5), 10000)

    def test_calculo_inconsistente(self):
        """Una rebaja mayor que el costo produce un cálculo inconsistente."""
        sala = ReservaSala("Sala", 10000, capacidad=10)
        self.assertEqual(sala.calcular_costo(2, rebaja=5000), 15000)
        with self.assertRaises(CalculoInconsistenteError):
            sala.calcular_costo(1, rebaja=50000)

    def test_sobrecarga_cotizar(self):
        """Cotizar() acepta int, float, list y dict."""
        sala = ReservaSala("Sala", 10000, capacidad=10)
        self.assertEqual(sala.cotizar(1), 11900)
        self.assertEqual(sala.cotizar(1.5), 17850)
        self.assertEqual(sala.cotizar([1, 1]), 23800)
        self.assertEqual(sala.cotizar({"horas": 1, "impuesto": 0}), 10000)
        with self.assertRaises(ValidacionError):
            sala.cotizar("dos horas")


class PruebasReserva(unittest.TestCase):
    """Pruebas del ciclo de vida de una reserva."""

    def setUp(self):
        """Datos comunes para cada prueba."""
        self.cliente = Cliente("Ana Torres", "1094567890", "ana@correo.com")
        self.sala = ReservaSala("Sala", 10000, capacidad=10)

    def test_flujo_completo(self):
        """PENDIENTE -> CONFIRMADA -> PROCESADA."""
        r = Reserva(self.cliente, self.sala, 2)
        r.confirmar()
        self.assertEqual(r.procesar(), 23800)
        self.assertIs(r.estado, EstadoReserva.PROCESADA)

    def test_servicio_no_disponible(self):
        """No se reserva un servicio deshabilitado."""
        self.sala.cambiar_disponibilidad(False)
        with self.assertRaises(ServicioNoDisponibleError):
            Reserva(self.cliente, self.sala, 2)

    def test_transicion_no_permitida(self):
        """No se procesa una reserva cancelada."""
        r = Reserva(self.cliente, self.sala, 2)
        r.cancelar()
        with self.assertRaises(OperacionNoPermitidaError):
            r.confirmar()

    def test_excepcion_encadenada(self):
        """El error de cálculo queda como causa."""
        r = Reserva(self.cliente, self.sala, 2)
        r.confirmar()
        with self.assertRaises(ReservaError) as ctx:
            r.procesar(descuento=2)
        self.assertIsInstance(ctx.exception.__cause__, ValidacionError)


class PruebasSistema(unittest.TestCase):
    """Pruebas de la tolerancia a errores y del inventario del sistema."""

    def test_inventario(self):
        """Alquilar descuenta el stock, cancelar lo repone y pedir de más falla."""
        s = SistemaGestion()
        cliente = s.registrar_cliente(nombre="Ana Torres", documento="1094567890", email="a@b.co")
        laptops = s.crear_servicio("equipo", nombre="Laptop", tarifa_hora=20000, cantidad=4)
        reserva = s.crear_reserva(cliente, laptops, 2)
        self.assertEqual(s.inventario["Laptop"], 6)    # 10 - 4
        s.cancelar_reserva(reserva)
        self.assertEqual(s.inventario["Laptop"], 10)   # Se repone al cancelar
        kits = s.crear_servicio("equipo", nombre="Kit VR", tarifa_hora=20000, cantidad=5)
        self.assertIsNone(s.crear_reserva(cliente, kits, 2))   # Solo hay 3 kits

    def test_sala_con_proyector(self):
        """El proyector suma $15.000 por hora."""
        sala = ReservaSala("Sala", 50000, capacidad=10, con_proyector=True)
        self.assertEqual(sala.calcular_costo(2), 130000)   # 50.000 x 2 + 15.000 x 2

    def test_sistema_no_se_detiene(self):
        """Los errores se cuentan y el sistema sigue."""
        s = SistemaGestion()
        self.assertIsNone(s.registrar_cliente(nombre="X", documento="1", email="mal"))
        self.assertIsNone(s.crear_servicio("inexistente", nombre="Y", tarifa_hora=1))
        self.assertIsNotNone(s.registrar_cliente(nombre="Ana Torres", documento="1094567890", email="a@b.co"))
        self.assertEqual(s.errores, 2)


if __name__ == "__main__":
    unittest.main()
