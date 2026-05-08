"""
Módulo con la clase Cliente.
Autor: Integrante Lina Alejandra Novoa Aguilar - Desarrollador de Clientes
Descripción: Clase que representa un cliente del sistema Software FJ,
             con encapsulación de datos y validaciones estrictas de
             nombre, documento, correo y teléfono.
"""

import re
from clases.entidad import Entidad
from excepciones.excepciones import (
    ErrorCliente,
    ErrorValidacion,
    ErrorParametroFaltante,
)


class Cliente(Entidad):
    """
    Clase que representa un cliente registrado en el sistema Software FJ.

    Hereda de: Entidad
    Implementa:
    - Encapsulación: todos los atributos son privados con propiedades
    - Validaciones estrictas: nombre, documento, correo, teléfono
    - Manejo de excepciones: try/except, try/except/else, try/except/finally
    """

    def __init__(
        self,
        nombre: str,
        documento: str,
        correo: str,
        telefono: str
    ):
        """
        Crea un nuevo cliente validando todos sus datos.

        Args:
            nombre    (str): Nombre completo del cliente.
            documento (str): Número de documento (cédula).
            correo    (str): Correo electrónico del cliente.
            telefono  (str): Número de teléfono del cliente.

        Raises:
            ErrorParametroFaltante: Si algún campo está vacío o es None.
            ErrorValidacion:        Si algún campo no cumple el formato.
        """
        # Primero validamos antes de llamar al padre
        self._validar_parametros_iniciales(nombre, documento, correo, telefono)

        super().__init__(nombre)

        self.__documento: str = documento
        self.__correo: str = correo
        self.__telefono: str = telefono
        self.__activo: bool = True
        self.__reservas: list = []

    # Validación interna de parámetros iniciales 

    def _validar_parametros_iniciales(
        self,
        nombre: str,
        documento: str,
        correo: str,
        telefono: str
    ) -> None:
        """
        Valida que ningún parámetro sea None o vacío antes de crear el objeto.
        Usa try/except/finally.
        """
        campos = {
            "nombre": nombre,
            "documento": documento,
            "correo": correo,
            "telefono": telefono,
        }
        try:
            for campo, valor in campos.items():
                if valor is None:
                    raise ErrorParametroFaltante(campo)
                if not isinstance(valor, str) or valor.strip() == "":
                    raise ErrorValidacion(campo, "no puede estar vacío")
        except (ErrorParametroFaltante, ErrorValidacion):
            raise
        except Exception as e:
            raise ErrorCliente(
                f"Error inesperado al validar parámetros iniciales: {e}"
            ) from e
        finally:
            # Siempre se ejecuta: útil para registrar intentos de creación
            pass

    # Propiedades (encapsulación total) 

    @property
    def documento(self) -> str:
        return self.__documento

    @property
    def correo(self) -> str:
        return self.__correo

    @property
    def telefono(self) -> str:
        return self.__telefono

    @property
    def activo(self) -> bool:
        return self.__activo

    @property
    def reservas(self) -> list:
        """Retorna una copia de la lista de reservas (protección de datos)."""
        return list(self.__reservas)

    # Setters con validación 

    @documento.setter
    def documento(self, valor: str) -> None:
        self.__documento = self._validar_documento(valor)

    @correo.setter
    def correo(self, valor: str) -> None:
        self.__correo = self._validar_correo(valor)

    @telefono.setter
    def telefono(self, valor: str) -> None:
        self.__telefono = self._validar_telefono(valor)

    # Métodos de validación individual 

    @staticmethod
    def _validar_nombre(nombre: str) -> str:
        """Valida que el nombre tenga al menos 3 caracteres y solo letras/espacios."""
        try:
            if not nombre or not isinstance(nombre, str):
                raise ErrorValidacion("nombre", "debe ser una cadena de texto")
            nombre = nombre.strip()
            if len(nombre) < 3:
                raise ErrorValidacion("nombre", "debe tener al menos 3 caracteres")
            if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$", nombre):
                raise ErrorValidacion(
                    "nombre", "solo puede contener letras y espacios"
                )
        except ErrorValidacion:
            raise
        except Exception as e:
            raise ErrorCliente(f"Error validando nombre: {e}") from e
        else:
            return nombre

    @staticmethod
    def _validar_documento(documento: str) -> str:
        """Valida que el documento tenga entre 6 y 15 dígitos numéricos."""
        try:
            if not documento or not isinstance(documento, str):
                raise ErrorValidacion("documento", "debe ser una cadena de texto")
            documento = documento.strip()
            if not documento.isdigit():
                raise ErrorValidacion("documento", "solo debe contener dígitos")
            if not (6 <= len(documento) <= 15):
                raise ErrorValidacion(
                    "documento", "debe tener entre 6 y 15 dígitos"
                )
        except ErrorValidacion:
            raise
        except Exception as e:
            raise ErrorCliente(f"Error validando documento: {e}") from e
        else:
            return documento

    @staticmethod
    def _validar_correo(correo: str) -> str:
        """Valida que el correo tenga formato estándar (usuario@dominio.ext)."""
        try:
            if not correo or not isinstance(correo, str):
                raise ErrorValidacion("correo", "debe ser una cadena de texto")
            correo = correo.strip().lower()
            patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
            if not re.match(patron, correo):
                raise ErrorValidacion(
                    "correo", f"'{correo}' no tiene un formato válido"
                )
        except ErrorValidacion:
            raise
        except Exception as e:
            raise ErrorCliente(f"Error validando correo: {e}") from e
        else:
            return correo

    @staticmethod
    def _validar_telefono(telefono: str) -> str:
        """Valida que el teléfono tenga entre 7 y 15 dígitos (permite + al inicio)."""
        try:
            if not telefono or not isinstance(telefono, str):
                raise ErrorValidacion("telefono", "debe ser una cadena de texto")
            telefono = telefono.strip().replace(" ", "").replace("-", "")
            patron = r"^\+?\d{7,15}$"
            if not re.match(patron, telefono):
                raise ErrorValidacion(
                    "telefono",
                    f"'{telefono}' no tiene un formato válido (7-15 dígitos)"
                )
        except ErrorValidacion:
            raise
        except Exception as e:
            raise ErrorCliente(f"Error validando teléfono: {e}") from e
        else:
            return telefono

    # Método abstracto heredado: validar() 

    def validar(self) -> bool:
        """
        Valida todos los datos del cliente.
        Usa try/except/else/finally según lo requerido.

        Returns:
            bool: True si todos los datos son válidos.
        """
        try:
            self._validar_nombre(self._nombre)
            self._validar_documento(self.__documento)
            self._validar_correo(self.__correo)
            self._validar_telefono(self.__telefono)
        except (ErrorValidacion, ErrorCliente):
            raise
        except Exception as e:
            raise ErrorCliente(
                f"Error inesperado en validación completa del cliente: {e}"
            ) from e
        else:
            # Solo si no hubo excepciones
            return True
        finally:
            # Siempre se ejecuta
            pass

    # Método abstracto heredado: describir() 

    def describir(self) -> str:
        """Retorna una descripción completa del cliente."""
        estado = "Activo" if self.__activo else "Inactivo"
        return (
            f"Cliente #{self._id}\n"
            f"  Nombre   : {self._nombre}\n"
            f"  Documento: {self.__documento}\n"
            f"  Correo   : {self.__correo}\n"
            f"  Teléfono : {self.__telefono}\n"
            f"  Estado   : {estado}\n"
            f"  Reservas : {len(self.__reservas)}"
        )

    # Métodos de negocio 

    def agregar_reserva(self, reserva) -> None:
        """
        Agrega una reserva al historial del cliente.

        Args:
            reserva: Objeto de tipo Reserva.

        Raises:
            ErrorCliente: Si el cliente está inactivo o la reserva es None.
        """
        try:
            if not self.__activo:
                raise ErrorCliente(
                    f"El cliente '{self._nombre}' está inactivo y no puede reservar"
                )
            if reserva is None:
                raise ErrorParametroFaltante("reserva")
            self.__reservas.append(reserva)
        except (ErrorCliente, ErrorParametroFaltante):
            raise
        except Exception as e:
            raise ErrorCliente(
                f"Error al agregar reserva al cliente: {e}"
            ) from e

    def desactivar(self) -> None:
        """Desactiva el cliente en el sistema."""
        self.__activo = False

    def activar(self) -> None:
        """Reactiva el cliente en el sistema."""
        self.__activo = True

    # Representación 

    def __str__(self) -> str:
        return (
            f"[Cliente] {self._nombre} | "
            f"Doc: {self.__documento} | "
            f"Correo: {self.__correo} | "
            f"Tel: {self.__telefono}"
        )
    