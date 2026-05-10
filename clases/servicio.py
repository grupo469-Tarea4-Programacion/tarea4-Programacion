"""
Módulo con la clase abstracta Servicio.
Autor: Integrante Nasly Isabella Velez Muñoz.
Descripción: Define el contrato que deben cumplir todos los servicios
             especializados: reserva de sala, alquiler de equipos
             y asesoría especializada.
"""

from abc import abstractmethod
from clases.entidad import Entidad
from excepciones.excepciones import (
    ErrorServicio,
    ErrorServicioNoDisponible,
    ErrorParametroFaltante,
    ErrorCalculoInconsistente,
)


class Servicio(Entidad):
    """
    Clase abstracta que representa un servicio ofrecido por Software FJ.

    Hereda de: Entidad
    Implementa:
    - Polimorfismo: calcular_costo() y describir() son abstractos
    - Métodos sobrecargados: calcular_costo_con_impuesto(),
                             calcular_costo_con_descuento()
    - Manejo de excepciones: validar() usa try/except/else/finally
    """

    IMPUESTO_DEFAULT: float = 0.19  # IVA Colombia 19 %

    def __init__(self, nombre: str, precio_base: float, disponible: bool = True):
        """
        Inicializa un servicio.

        Args:
            nombre      (str):   Nombre del servicio.
            precio_base (float): Precio base por unidad de tiempo.
            disponible  (bool):  Indica si el servicio está activo.
        """
        super().__init__(nombre)
        self._precio_base: float = precio_base
        self._disponible: bool = disponible

    # Propiedades 

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise ErrorServicio("El campo 'disponible' debe ser True o False")
        self._disponible = valor

    # Métodos abstractos (polimorfismo) 

    @abstractmethod
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        """
        Calcula el costo base del servicio.

        Args:
            duracion (float): Duración en horas.
            **kwargs:         Parámetros adicionales específicos del servicio.

        Returns:
            float: Costo calculado.
        """
        pass

    @abstractmethod
    def describir(self) -> str:
        """Retorna la descripción completa del servicio."""
        pass

    # Validación con try/except/else/finally

    def validar(self) -> bool:
        """
        Valida que el servicio tenga datos correctos.
        Usa try/except/else/finally según lo requerido por la tarea.

        Returns:
            bool: True si el servicio es válido.

        Raises:
            ErrorServicio: Si algún dato es inválido.
        """
        try:
            if not self._nombre or not isinstance(self._nombre, str):
                raise ErrorServicio("El nombre del servicio es inválido o está vacío")
            if not isinstance(self._precio_base, (int, float)):
                raise ErrorServicio("El precio base debe ser un número")
            if self._precio_base <= 0:
                raise ErrorCalculoInconsistente(
                    f"precio_base={self._precio_base} debe ser mayor a 0"
                )
        except (ErrorServicio, ErrorCalculoInconsistente):
            raise   # Re-lanza para que el llamador la maneje
        except Exception as e:
            raise ErrorServicio(f"Error inesperado en validación: {e}") from e
        else:
            # Solo se ejecuta si NO hubo excepción
            return True
        finally:
            # Siempre se ejecuta (para logging en el futuro)
            pass

    # Métodos sobrecargados (variantes de cálculo de costo) 

    def calcular_costo_con_impuesto(
        self,
        duracion: float,
        impuesto: float = IMPUESTO_DEFAULT
    ) -> float:
        """
        Calcula el costo incluyendo impuesto (IVA).

        Args:
            duracion  (float): Duración en horas.
            impuesto  (float): Tasa de impuesto (por defecto 19 %).

        Returns:
            float: Costo total con impuesto.
        """
        try:
            if duracion is None:
                raise ErrorParametroFaltante("duracion")
            if duracion <= 0:
                raise ErrorCalculoInconsistente(
                    f"La duración debe ser > 0, se recibió {duracion}"
                )
            if not (0 <= impuesto <= 1):
                raise ErrorCalculoInconsistente(
                    f"El impuesto debe estar entre 0 y 1, se recibió {impuesto}"
                )
            if not self._disponible:
                raise ErrorServicioNoDisponible(self._nombre)

            costo_base = self.calcular_costo(duracion)
            return round(costo_base * (1 + impuesto), 2)

        except (ErrorParametroFaltante, ErrorCalculoInconsistente,
                ErrorServicioNoDisponible):
            raise
        except Exception as e:
            raise ErrorCalculoInconsistente(
                f"Fallo inesperado al calcular costo con impuesto: {e}"
            ) from e

    def calcular_costo_con_descuento(
        self,
        duracion: float,
        descuento: float = 0.0,
        aplicar_impuesto: bool = False
    ) -> float:
        """
        Calcula el costo aplicando un descuento y opcionalmente impuesto.

        Args:
            duracion         (float): Duración en horas.
            descuento        (float): Porcentaje de descuento entre 0 y 1.
            aplicar_impuesto (bool):  Si True, añade el IVA después del descuento.

        Returns:
            float: Costo final.
        """
        try:
            if not (0 <= descuento <= 1):
                raise ErrorCalculoInconsistente(
                    f"El descuento debe estar entre 0 y 1, se recibió {descuento}"
                )
            if not self._disponible:
                raise ErrorServicioNoDisponible(self._nombre)

            costo_base = self.calcular_costo(duracion)
            costo_con_descuento = costo_base * (1 - descuento)

            if aplicar_impuesto:
                costo_con_descuento *= (1 + self.IMPUESTO_DEFAULT)

            return round(costo_con_descuento, 2)

        except (ErrorCalculoInconsistente, ErrorServicioNoDisponible):
            raise
        except Exception as e:
            raise ErrorCalculoInconsistente(
                f"Fallo inesperado al calcular costo con descuento: {e}"
            ) from e

    # Representación 

    def __str__(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"[Servicio] {self._nombre} | "
            f"Precio base: ${self._precio_base:,.2f}/h | "
            f"{estado}"
        )