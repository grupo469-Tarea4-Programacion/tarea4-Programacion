"""
Módulo con el servicio de Reserva de Sala.
Autor: Integrante Nasly Isabella Velez Muñoz - Desarrollador de Servicios
Descripción: Servicio especializado para reservar salas de reuniones
             o conferencias en Software FJ.
"""

from clases.servicio import Servicio
from excepciones.excepciones import (
    ErrorServicio,
    ErrorCalculoInconsistente,
    ErrorParametroFaltante,
    ErrorServicioNoDisponible,
)


class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reuniones.

    Hereda de: Servicio -> Entidad
    Atributos propios:
    - capacidad_maxima: cuántas personas puede albergar la sala
    - tiene_proyector : si la sala cuenta con proyector incluido
    """

    COSTO_PROYECTOR_POR_HORA: float = 15_000.0  # Costo adicional por proyector

    def __init__(
        self,
        nombre: str,
        precio_base: float,
        capacidad_maxima: int,
        tiene_proyector: bool = False,
        disponible: bool = True
    ):
        """
        Crea un servicio de reserva de sala.

        Args:
            nombre           (str):  Nombre identificador de la sala.
            precio_base      (float): Precio por hora sin extras.
            capacidad_maxima (int):  Número máximo de personas.
            tiene_proyector  (bool): Si incluye proyector.
            disponible       (bool): Si está disponible para reservar.
        """
        super().__init__(nombre, precio_base, disponible)

        if not isinstance(capacidad_maxima, int) or capacidad_maxima <= 0:
            raise ErrorServicio(
                f"La capacidad máxima debe ser un entero positivo, "
                f"se recibió: {capacidad_maxima}"
            )

        self.__capacidad_maxima: int = capacidad_maxima
        self.__tiene_proyector: bool = tiene_proyector

    # Propiedades 

    @property
    def capacidad_maxima(self) -> int:
        return self.__capacidad_maxima

    @property
    def tiene_proyector(self) -> bool:
        return self.__tiene_proyector

    # Métodos abstractos implementados (polimorfismo) 

    def calcular_costo(self, duracion: float, **kwargs) -> float:
        """
        Calcula el costo de la reserva de sala.

        Args:
            duracion (float): Duración en horas.
            **kwargs:
                num_personas (int): Número de asistentes (opcional,
                                    verifica que no exceda la capacidad).

        Returns:
            float: Costo total de la sala.

        Raises:
            ErrorParametroFaltante:    Si duracion es None.
            ErrorCalculoInconsistente: Si duracion <= 0 o supera capacidad.
            ErrorServicioNoDisponible: Si la sala no está disponible.
        """
        try:
            if duracion is None:
                raise ErrorParametroFaltante("duracion")
            if not isinstance(duracion, (int, float)) or duracion <= 0:
                raise ErrorCalculoInconsistente(
                    f"La duración debe ser mayor a 0, se recibió: {duracion}"
                )
            if not self._disponible:
                raise ErrorServicioNoDisponible(self._nombre)

            num_personas = kwargs.get("num_personas", 1)
            if num_personas > self.__capacidad_maxima:
                raise ErrorCalculoInconsistente(
                    f"El número de personas ({num_personas}) supera la "
                    f"capacidad máxima ({self.__capacidad_maxima})"
                )

            costo = self._precio_base * duracion

            if self.__tiene_proyector:
                costo += self.COSTO_PROYECTOR_POR_HORA * duracion

        except (ErrorParametroFaltante, ErrorCalculoInconsistente,
                ErrorServicioNoDisponible):
            raise
        except Exception as e:
            raise ErrorServicio(
                f"Error inesperado al calcular costo de sala: {e}"
            ) from e
        else:
            return round(costo, 2)
        finally:
            pass

    def describir(self) -> str:
        """Retorna descripción completa de la sala."""
        proyector = "Sí" if self.__tiene_proyector else "No"
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Servicio: Reserva de Sala\n"
            f"  Nombre          : {self._nombre}\n"
            f"  Precio base/hora: ${self._precio_base:,.2f}\n"
            f"  Capacidad máxima: {self.__capacidad_maxima} personas\n"
            f"  Proyector       : {proyector}\n"
            f"  Estado          : {estado}"
        )

    def validar(self) -> bool:
        """Valida los datos propios de la sala además de los del servicio."""
        try:
            super().validar()
            if self.__capacidad_maxima <= 0:
                raise ErrorServicio("La capacidad máxima debe ser mayor a 0")
        except ErrorServicio:
            raise
        except Exception as e:
            raise ErrorServicio(f"Error al validar ReservaSala: {e}") from e
        else:
            return True
        finally:
            pass

    def __str__(self) -> str:
        return (
            f"[ReservaSala] {self._nombre} | "
            f"Capacidad: {self.__capacidad_maxima} personas | "
            f"${self._precio_base:,.2f}/h"
        )
    