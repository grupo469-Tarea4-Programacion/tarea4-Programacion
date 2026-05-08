"""
Módulo con la clase Reserva.
Autor: Integrante Lina Alejandra Novoa Aguilar - Responsable de Calidad y Errores
Descripción: Clase que integra Cliente y Servicio en una reserva,
             con métodos de confirmación, cancelación y procesamiento,
             y manejo robusto de excepciones en todo el flujo.
"""

from datetime import datetime
from clases.cliente import Cliente
from clases.servicio import Servicio
from excepciones.excepciones import (
    ErrorReserva,
    ErrorReservaInvalida,
    ErrorOperacionNoPermitida,
    ErrorParametroFaltante,
    ErrorServicioNoDisponible,
    ErrorCalculoInconsistente,
)


class Reserva:
    """
    Clase que representa una reserva en el sistema Software FJ.

    Integra:
    - Un Cliente válido y activo
    - Un Servicio disponible
    - Una duración en horas
    - Un estado: 'pendiente', 'confirmada', 'cancelada', 'procesada'

    Implementa:
    - Confirmación, cancelación y procesamiento con excepciones
    - Registro automático en el sistema de logs
    - Manejo de bloques try/except, try/except/else, try/except/finally
    """

    ESTADOS_VALIDOS = ["pendiente", "confirmada", "cancelada", "procesada"]
    _contador_reservas: int = 0

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        **kwargs
    ):
        """
        Crea una nueva reserva.

        Args:
            cliente  (Cliente):  Cliente que realiza la reserva.
            servicio (Servicio): Servicio que se va a reservar.
            duracion (float):    Duración en horas.
            **kwargs:            Parámetros extra para el cálculo de costo.

        Raises:
            ErrorParametroFaltante: Si cliente, servicio o duracion son None.
            ErrorReservaInvalida:   Si los datos no son válidos.
        """
        from logger.logger import Logger
        self._logger = Logger()

        try:
            self._validar_parametros(cliente, servicio, duracion)

            Reserva._contador_reservas += 1
            self.__id: int = Reserva._contador_reservas
            self.__cliente: Cliente = cliente
            self.__servicio: Servicio = servicio
            self.__duracion: float = duracion
            self.__kwargs: dict = kwargs
            self.__estado: str = "pendiente"
            self.__fecha_creacion: datetime = datetime.now()
            self.__fecha_confirmacion: datetime = None
            self.__costo_total: float = 0.0

            # Registrar al cliente esta reserva
            cliente.agregar_reserva(self)

            self._logger.info(
                f"Reserva #{self.__id} creada | "
                f"Cliente: {cliente.nombre} | "
                f"Servicio: {servicio.nombre} | "
                f"Duración: {duracion}h"
            )

        except (ErrorParametroFaltante, ErrorReservaInvalida,
                ErrorServicioNoDisponible):
            raise
        except Exception as e:
            raise ErrorReservaInvalida(
                f"Error inesperado al crear la reserva: {e}"
            ) from e

    # Validación inicial 

    @staticmethod
    def _validar_parametros(
        cliente: Cliente,
        servicio: Servicio,
        duracion: float
    ) -> None:
        """
        Valida los parámetros obligatorios de la reserva.
        Usa try/except/else/finally.
        """
        try:
            if cliente is None:
                raise ErrorParametroFaltante("cliente")
            if servicio is None:
                raise ErrorParametroFaltante("servicio")
            if duracion is None:
                raise ErrorParametroFaltante("duracion")
            if not isinstance(cliente, Cliente):
                raise ErrorReservaInvalida("El parámetro 'cliente' no es una instancia de Cliente")
            if not isinstance(servicio, Servicio):
                raise ErrorReservaInvalida("El parámetro 'servicio' no es una instancia de Servicio")
            if not isinstance(duracion, (int, float)) or duracion <= 0:
                raise ErrorReservaInvalida(
                    f"La duración debe ser un número mayor a 0, "
                    f"se recibió: {duracion}"
                )
            if not cliente.activo:
                raise ErrorReservaInvalida(
                    f"El cliente '{cliente.nombre}' está inactivo"
                )
            if not servicio.disponible:
                raise ErrorServicioNoDisponible(servicio.nombre)

        except (ErrorParametroFaltante, ErrorReservaInvalida,
                ErrorServicioNoDisponible):
            raise
        except Exception as e:
            raise ErrorReservaInvalida(
                f"Error inesperado en validación de reserva: {e}"
            ) from e
        else:
            pass  # Todo correcto
        finally:
            pass  # Punto de log futuro

    # Propiedades 

    @property
    def id(self) -> int:
        return self.__id

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def duracion(self) -> float:
        return self.__duracion

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def costo_total(self) -> float:
        return self.__costo_total

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    # Métodos de negocio

    def confirmar(self) -> str:
        """
        Confirma la reserva y calcula el costo total.

        Returns:
            str: Mensaje de confirmación con el costo.

        Raises:
            ErrorOperacionNoPermitida: Si la reserva no está en estado 'pendiente'.
            ErrorCalculoInconsistente: Si falla el cálculo del costo.
        """
        try:
            if self.__estado != "pendiente":
                raise ErrorOperacionNoPermitida(
                    "confirmar",
                    f"la reserva está en estado '{self.__estado}'"
                )

            self.__costo_total = self.__servicio.calcular_costo(
                self.__duracion, **self.__kwargs
            )

            if self.__costo_total <= 0:
                raise ErrorCalculoInconsistente(
                    f"El costo calculado es inválido: {self.__costo_total}"
                )

        except (ErrorOperacionNoPermitida, ErrorCalculoInconsistente,
                ErrorServicioNoDisponible):
            self._logger.error(
                f"Error al confirmar Reserva #{self.__id}: "
                f"{self.__estado}"
            )
            raise
        except Exception as e:
            raise ErrorReserva(
                f"Error inesperado al confirmar reserva #{self.__id}: {e}"
            ) from e
        else:
            self.__estado = "confirmada"
            self.__fecha_confirmacion = datetime.now()
            mensaje = (
                f"Reserva #{self.__id} confirmada | "
                f"Cliente: {self.__cliente.nombre} | "
                f"Costo total: ${self.__costo_total:,.2f}"
            )
            self._logger.info(mensaje)
            return mensaje
        finally:
            pass

    def cancelar(self, motivo: str = "Sin motivo especificado") -> str:
        """
        Cancela la reserva.

        Args:
            motivo (str): Razón de la cancelación.

        Returns:
            str: Mensaje de cancelación.

        Raises:
            ErrorOperacionNoPermitida: Si la reserva ya fue procesada o cancelada.
        """
        try:
            if self.__estado in ["cancelada", "procesada"]:
                raise ErrorOperacionNoPermitida(
                    "cancelar",
                    f"la reserva ya está en estado '{self.__estado}'"
                )

        except ErrorOperacionNoPermitida:
            self._logger.error(
                f"Cancelación inválida en Reserva #{self.__id}: "
                f"estado actual '{self.__estado}'"
            )
            raise
        except Exception as e:
            raise ErrorReserva(
                f"Error inesperado al cancelar reserva #{self.__id}: {e}"
            ) from e
        else:
            self.__estado = "cancelada"
            mensaje = (
                f"Reserva #{self.__id} cancelada | "
                f"Cliente: {self.__cliente.nombre} | "
                f"Motivo: {motivo}"
            )
            self._logger.info(mensaje)
            return mensaje
        finally:
            pass

    def procesar(self) -> str:
        """
        Procesa la reserva (marca como completada y ejecutada).

        Returns:
            str: Mensaje de procesamiento.

        Raises:
            ErrorOperacionNoPermitida: Si la reserva no está confirmada.
        """
        try:
            if self.__estado != "confirmada":
                raise ErrorOperacionNoPermitida(
                    "procesar",
                    f"solo se pueden procesar reservas confirmadas, "
                    f"estado actual: '{self.__estado}'"
                )

        except ErrorOperacionNoPermitida:
            self._logger.error(
                f"Procesamiento inválido en Reserva #{self.__id}: "
                f"estado actual '{self.__estado}'"
            )
            raise
        except Exception as e:
            raise ErrorReserva(
                f"Error inesperado al procesar reserva #{self.__id}: {e}"
            ) from e
        else:
            self.__estado = "procesada"
            mensaje = (
                f"Reserva #{self.__id} procesada exitosamente | "
                f"Cliente: {self.__cliente.nombre} | "
                f"Servicio: {self.__servicio.nombre} | "
                f"Duración: {self.__duracion}h | "
                f"Total pagado: ${self.__costo_total:,.2f}"
            )
            self._logger.info(mensaje)
            return mensaje
        finally:
            pass

    def describir(self) -> str:
        """Retorna una descripción completa del estado de la reserva."""
        fecha_str = self.__fecha_creacion.strftime("%Y-%m-%d %H:%M:%S")
        confirmacion_str = (
            self.__fecha_confirmacion.strftime("%Y-%m-%d %H:%M:%S")
            if self.__fecha_confirmacion else "No confirmada aún"
        )
        return (
            f"Reserva #{self.__id}\n"
            f"  Cliente       : {self.__cliente.nombre}\n"
            f"  Servicio      : {self.__servicio.nombre}\n"
            f"  Duración      : {self.__duracion}h\n"
            f"  Estado        : {self.__estado.upper()}\n"
            f"  Costo total   : ${self.__costo_total:,.2f}\n"
            f"  Fecha creación: {fecha_str}\n"
            f"  Confirmación  : {confirmacion_str}"
        )

    def __str__(self) -> str:
        return (
            f"[Reserva #{self.__id}] "
            f"{self.__cliente.nombre} -> {self.__servicio.nombre} | "
            f"{self.__duracion}h | Estado: {self.__estado.upper()}"
        )
    