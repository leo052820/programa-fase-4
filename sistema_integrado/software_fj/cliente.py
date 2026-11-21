"""
cliente.py
Clase Cliente con datos personales encapsulados y validaciones estrictas.
"""

import re                                              # Expresiones regulares para validar formatos
from .entidad import EntidadBase                       # Clase abstracta de la que hereda Cliente
from .excepciones import ValidacionError, ParametroFaltanteError  # Errores que puede lanzar

PATRON_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")   # Formato básico de correo: usuario@dominio.ext
PATRON_TELEFONO = re.compile(r"^\d{7,10}$")                 # Teléfono de 7 a 10 dígitos
PATRON_DOCUMENTO = re.compile(r"^\d{6,12}$")                # Documento de 6 a 12 dígitos


class Cliente(EntidadBase):                            # Cliente hereda ID y fecha de EntidadBase
    """Cliente de Software FJ. Sus datos solo cambian a través de propiedades validadas."""

    def __init__(self, nombre, documento, email, telefono=None):
        """Crea un cliente validando cada dato; el teléfono es opcional."""
        self.nombre = nombre                           # Usa el setter, que valida el nombre
        self.documento = documento                     # Usa el setter, que valida el documento
        self.email = email                             # Usa el setter, que valida el correo
        self.telefono = telefono                       # Usa el setter, que valida el teléfono
        super().__init__("CLI")                        # Solo si todo es válido se asigna el ID

    # ----- Propiedades con validación (encapsulación) -----
    @property
    def nombre(self):
        """Lectura del nombre."""
        return self.__nombre                           # Atributo privado (doble guion bajo)

    @nombre.setter
    def nombre(self, valor):
        """Escritura del nombre con validación."""
        if valor is None:                              # El nombre es obligatorio
            raise ParametroFaltanteError("nombre")
        valor = str(valor).strip()                     # Quita espacios al inicio y al final
        if len(valor) < 3:                             # Debe tener al menos 3 caracteres
            raise ValidacionError("nombre", "debe tener al menos 3 caracteres")
        if not all(c.isalpha() or c.isspace() for c in valor):   # Solo letras y espacios
            raise ValidacionError("nombre", "solo puede contener letras y espacios")
        self.__nombre = valor.title()                  # Guarda el nombre con mayúscula inicial

    @property
    def documento(self):
        """Lectura del documento."""
        return self.__documento

    @documento.setter
    def documento(self, valor):
        """Escritura del documento con validación."""
        if valor is None:                              # El documento es obligatorio
            raise ParametroFaltanteError("documento")
        valor = str(valor).strip()                     # Lo convierte a texto sin espacios
        if not PATRON_DOCUMENTO.match(valor):          # Debe tener entre 6 y 12 dígitos
            raise ValidacionError("documento", "debe tener entre 6 y 12 dígitos")
        self.__documento = valor                       # Guarda el documento validado

    @property
    def email(self):
        """Lectura del correo."""
        return self.__email

    @email.setter
    def email(self, valor):
        """Escritura del correo con validación."""
        if not valor:                                  # El correo es obligatorio
            raise ParametroFaltanteError("email")
        valor = str(valor).strip().lower()             # Normaliza a minúsculas
        if not PATRON_EMAIL.match(valor):              # Verifica el formato usuario@dominio.ext
            raise ValidacionError("email", f"formato inválido: {valor}")
        self.__email = valor                           # Guarda el correo validado

    @property
    def telefono(self):
        """Lectura del teléfono."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        """Escritura del teléfono con validación."""
        if valor is None:                              # El teléfono es opcional
            self.__telefono = None                     # Se guarda vacío
            return
        valor = str(valor).strip()                     # Lo convierte a texto sin espacios
        if not PATRON_TELEFONO.match(valor):           # Debe tener entre 7 y 10 dígitos
            raise ValidacionError("telefono", "debe tener entre 7 y 10 dígitos")
        self.__telefono = valor                        # Guarda el teléfono validado

    # ----- Métodos heredados de EntidadBase -----
    def validar(self):
        """Revalida todos los datos del cliente."""
        self.nombre = self.nombre                      # Cada asignación vuelve a pasar por su setter
        self.documento = self.documento
        self.email = self.email
        self.telefono = self.telefono
        return True                                    # Si no hubo excepción, el cliente es válido

    def describir(self):
        """Implementación polimórfica de describir()."""
        tel = self.telefono or "sin teléfono"          # Texto alternativo si no hay teléfono
        return f"{self.id} | {self.nombre} | Doc. {self.documento} | {self.email} | {tel}"
