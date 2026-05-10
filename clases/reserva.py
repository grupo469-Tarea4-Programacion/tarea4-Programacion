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
                raise ErrorReservaInvalida("The 'cliente' parameter is not an instance of Cliente")
            if not isinstance(servicio, Servicio):
                raise ErrorReservaInvalida("The 'servicio' parameter is not an instance of Servicio")
            if not isinstance(duracion, (int, float)) or duracion <= 0:
                raise ErrorReservaInvalida(
                    f"Duration must be a number greater than 0, "
                    f"received: {duracion}"
                )
            if not cliente.activo:
                raise ErrorReservaInvalida(
                    f"The client '{cliente.nombre}' is inactive"
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
                    f"the reservation is in state '{self.__estado}'"
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
                f"Error confirming Reservation #{self.__id}: "
                f"{self.__estado}"
            )
            raise
        except Exception as e:
            raise ErrorReserva(
                f"Unexpected error while confirming reservation #{self.__id}: {e}"
            ) from e
        else:
            self.__estado = "confirmada"
            self.__fecha_confirmacion = datetime.now()
            mensaje = (
                f"Reservation #{self.__id} confirmed | "
                f"Client: {self.__cliente.nombre} | "
                f"Total cost: ${self.__costo_total:,.2f}"
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
                    f"the reservation is already in state '{self.__estado}'"
                )

        except ErrorOperacionNoPermitida:
            self._logger.error(
                f"Invalid cancellation in Reservation #{self.__id}: "
                f"estado actual '{self.__estado}'"
            )
            raise
        except Exception as e:
            raise ErrorReserva(
                f"Unexpected error while cancelling reservation #{self.__id}: {e}"
            ) from e
        else:
            self.__estado = "cancelada"
            mensaje = (
                f"Reservation #{self.__id} cancelled | "
                f"Client: {self.__cliente.nombre} | "
                f"Reason: {motivo}"
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
                    f"only confirmed reservations can be processed, "
                    f"current state: '{self.__estado}'"
                )

        except ErrorOperacionNoPermitida:
            self._logger.error(
                f"Invalid processing in Reservation #{self.__id}: "
                f"estado actual '{self.__estado}'"
            )
            raise
        except Exception as e:
            raise ErrorReserva(
                f"Unexpected error while processing reservation #{self.__id}: {e}"
            ) from e
        else:
            self.__estado = "procesada"
            mensaje = (
                f"Reservation #{self.__id} processed successfully | "
                f"Client: {self.__cliente.nombre} | "
                f"Service: {self.__servicio.nombre} | "
                f"Duration: {self.__duracion}h | "
                f"Total paid: ${self.__costo_total:,.2f}"
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
            if self.__fecha_confirmacion else "Not confirmed yet"
        )
        return (
            f"Reservation #{self.__id}\n"
            f"  Client       : {self.__cliente.nombre}\n"
            f"  Service      : {self.__servicio.nombre}\n"
            f"  Duration     : {self.__duracion}h\n"
            f"  Status       : {self.__estado.upper()}\n"
            f"  Total cost   : ${self.__costo_total:,.2f}\n"
            f"  Created at   : {fecha_str}\n"
            f"  Confirmation : {confirmacion_str}"
        )

    def __str__(self) -> str:
        return (
            f"[Reservation #{self.__id}] "
            f"{self.__cliente.nombre} -> {self.__servicio.nombre} | "
            f"{self.__duracion}h | Status: {self.__estado.upper()}"
        ) 