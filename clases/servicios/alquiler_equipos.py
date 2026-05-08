"""
Módulo con el servicio de Alquiler de Equipos.
Autor: Integrante Nasly Isabella Velez Muñoz - Desarrollador de Servicios
Descripción: Servicio especializado para alquilar equipos tecnológicos
             (portátiles, cámaras, proyectores, etc.) en Software FJ.
"""

from clases.servicio import Servicio
from excepciones.excepciones import (
    ErrorServicio,
    ErrorCalculoInconsistente,
    ErrorParametroFaltante,
    ErrorServicioNoDisponible,
)


class AlquilerEquipos(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.

    Hereda de: Servicio -> Entidad
    Atributos propios:
    - tipo_equipo      : descripción del equipo (ej: 'Portátil HP')
    - unidades_disponibles: cantidad de unidades disponibles para alquilar
    - requiere_deposito: si el cliente debe pagar depósito de garantía
    """

    PORCENTAJE_DEPOSITO: float = 0.30  # 30% del costo como depósito

    def __init__(
        self,
        nombre: str,
        precio_base: float,
        tipo_equipo: str,
        unidades_disponibles: int,
        requiere_deposito: bool = True,
        disponible: bool = True
    ):
        """
        Crea un servicio de alquiler de equipos.

        Args:
            nombre               (str):  Nombre del servicio de alquiler.
            precio_base          (float): Precio por hora por unidad.
            tipo_equipo          (str):  Descripción del tipo de equipo.
            unidades_disponibles (int):  Unidades disponibles en inventario.
            requiere_deposito    (bool): Si exige depósito de garantía.
            disponible           (bool): Si el servicio está activo.
        """
        super().__init__(nombre, precio_base, disponible)

        if not tipo_equipo or not isinstance(tipo_equipo, str):
            raise ErrorServicio("El tipo de equipo no puede estar vacío")
        if not isinstance(unidades_disponibles, int) or unidades_disponibles < 0:
            raise ErrorServicio(
                f"Las unidades disponibles deben ser un entero >= 0, "
                f"se recibió: {unidades_disponibles}"
            )

        self.__tipo_equipo: str = tipo_equipo.strip()
        self.__unidades_disponibles: int = unidades_disponibles
        self.__requiere_deposito: bool = requiere_deposito

    # Propiedades 

    @property
    def tipo_equipo(self) -> str:
        return self.__tipo_equipo

    @property
    def unidades_disponibles(self) -> int:
        return self.__unidades_disponibles

    @property
    def requiere_deposito(self) -> bool:
        return self.__requiere_deposito

    # Métodos abstractos implementados (polimorfismo) 

    def calcular_costo(self, duracion: float, **kwargs) -> float:
        """
        Calcula el costo del alquiler de equipos.

        Args:
            duracion (float): Duración en horas.
            **kwargs:
                cantidad (int): Número de unidades a alquilar (default 1).

        Returns:
            float: Costo total del alquiler.

        Raises:
            ErrorParametroFaltante:    Si duracion es None.
            ErrorCalculoInconsistente: Si duracion <= 0 o sin unidades.
            ErrorServicioNoDisponible: Si el servicio no está disponible.
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

            cantidad = kwargs.get("cantidad", 1)

            if not isinstance(cantidad, int) or cantidad <= 0:
                raise ErrorCalculoInconsistente(
                    f"La cantidad debe ser un entero positivo, "
                    f"se recibió: {cantidad}"
                )
            if cantidad > self.__unidades_disponibles:
                raise ErrorCalculoInconsistente(
                    f"Se solicitaron {cantidad} unidades pero solo hay "
                    f"{self.__unidades_disponibles} disponibles"
                )

            costo = self._precio_base * duracion * cantidad

        except (ErrorParametroFaltante, ErrorCalculoInconsistente,
                ErrorServicioNoDisponible):
            raise
        except Exception as e:
            raise ErrorServicio(
                f"Error inesperado al calcular costo de alquiler: {e}"
            ) from e
        else:
            return round(costo, 2)
        finally:
            pass

    def calcular_deposito(self, duracion: float, cantidad: int = 1) -> float:
        """
        Calcula el valor del depósito de garantía si aplica.

        Args:
            duracion (float): Duración en horas.
            cantidad (int):   Número de unidades.

        Returns:
            float: Valor del depósito (0 si no requiere depósito).
        """
        try:
            if not self.__requiere_deposito:
                return 0.0
            costo_base = self.calcular_costo(duracion, cantidad=cantidad)
            return round(costo_base * self.PORCENTAJE_DEPOSITO, 2)
        except ErrorServicio:
            raise
        except Exception as e:
            raise ErrorCalculoInconsistente(
                f"Error al calcular depósito: {e}"
            ) from e

    def reducir_unidades(self, cantidad: int = 1) -> None:
        """Reduce el inventario al confirmar un alquiler."""
        try:
            if cantidad > self.__unidades_disponibles:
                raise ErrorCalculoInconsistente(
                    "No hay suficientes unidades disponibles para reducir"
                )
            self.__unidades_disponibles -= cantidad
            if self.__unidades_disponibles == 0:
                self._disponible = False
        except ErrorCalculoInconsistente:
            raise
        except Exception as e:
            raise ErrorServicio(f"Error al reducir unidades: {e}") from e

    def describir(self) -> str:
        """Retorna descripción completa del servicio de alquiler."""
        deposito = "Sí" if self.__requiere_deposito else "No"
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Servicio: Alquiler de Equipos\n"
            f"  Nombre          : {self._nombre}\n"
            f"  Tipo de equipo  : {self.__tipo_equipo}\n"
            f"  Precio base/hora: ${self._precio_base:,.2f} por unidad\n"
            f"  Unidades disp.  : {self.__unidades_disponibles}\n"
            f"  Requiere depósito: {deposito}\n"
            f"  Estado          : {estado}"
        )

    def validar(self) -> bool:
        """Valida los datos propios del alquiler además de los del servicio."""
        try:
            super().validar()
            if not self.__tipo_equipo:
                raise ErrorServicio("El tipo de equipo no puede estar vacío")
            if self.__unidades_disponibles < 0:
                raise ErrorServicio("Las unidades disponibles no pueden ser negativas")
        except ErrorServicio:
            raise
        except Exception as e:
            raise ErrorServicio(f"Error al validar AlquilerEquipos: {e}") from e
        else:
            return True
        finally:
            pass

    def __str__(self) -> str:
        return (
            f"[AlquilerEquipos] {self.__tipo_equipo} | "
            f"Unidades: {self.__unidades_disponibles} | "
            f"${self._precio_base:,.2f}/h por unidad"
        )
    