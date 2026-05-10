"""
Módulo con el servicio de Asesoría Especializada.
Autor: Integrante Nasly Isabella Velez Muñoz - Desarrollador de Servicios
Descripción: Servicio especializado de consultoría y asesorías técnicas
             o profesionales ofrecidas por Software FJ.
"""

from clases.servicio import Servicio
from excepciones.excepciones import (
    ErrorServicio,
    ErrorCalculoInconsistente,
    ErrorParametroFaltante,
    ErrorServicioNoDisponible,
)


class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría técnica o profesional especializada.

    Hereda de: Servicio -> Entidad
    Atributos propios:
    - area_especializacion: rama de la asesoría (ej: 'Ciberseguridad')
    - nivel : nivel del asesor ('junior', 'senior', 'experto')
    - duracion_minima : mínimo de horas que se puede contratar
    """

    TARIFAS_NIVEL: dict = {
        "junior" : 1.0,   # Multiplicador base
        "senior" : 1.5,   # 50% más caro
        "experto": 2.0,   # El doble
    }

    NIVELES_VALIDOS = list(TARIFAS_NIVEL.keys())

    def __init__(
        self,
        nombre: str,
        precio_base: float,
        area_especializacion: str,
        nivel: str = "junior",
        duracion_minima: float = 1.0,
        disponible: bool = True
    ):
        """
        Crea un servicio de asesoría especializada.

        Args:
            nombre               (str):   Nombre del servicio.
            precio_base          (float):  Precio base por hora (nivel junior).
            area_especializacion (str):   Área temática de la asesoría.
            nivel                (str):   Nivel del asesor.
            duracion_minima      (float):  Mínimo de horas a contratar.
            disponible           (bool):  Si el servicio está activo.
        """
        super().__init__(nombre, precio_base, disponible)

        nivel = nivel.strip().lower()
        if nivel not in self.NIVELES_VALIDOS:
            raise ErrorServicio(
                f"Nivel '{nivel}' no válido. "
                f"Opciones: {self.NIVELES_VALIDOS}"
            )
        if not area_especializacion or not isinstance(area_especializacion, str):
            raise ErrorServicio("El área de especialización no puede estar vacía")
        if not isinstance(duracion_minima, (int, float)) or duracion_minima <= 0:
            raise ErrorServicio(
                f"La duración mínima debe ser mayor a 0, "
                f"se recibió: {duracion_minima}"
            )

        self.__area_especializacion: str = area_especializacion.strip()
        self.__nivel: str = nivel
        self.__duracion_minima: float = duracion_minima

        # Validación final del objeto
        self.validar()

    # Propiedades 

    @property
    def area_especializacion(self) -> str:
        return self.__area_especializacion

    @property
    def nivel(self) -> str:
        return self.__nivel

    @property
    def duracion_minima(self) -> float:
        return self.__duracion_minima

    # Métodos abstractos implementados (polimorfismo) 

    def calcular_costo(self, duracion: float, **kwargs) -> float:
        """
        Calcula el costo de la asesoría según duración y nivel del asesor.

        Args:
            duracion (float): Duración en horas.
            **kwargs:
                urgente (bool): Si la asesoría es urgente (recargo 20%).

        Returns:
            float: Costo total de la asesoría.

        Raises:
            ErrorParametroFaltante:    Si duracion es None.
            ErrorCalculoInconsistente: Si duración < mínimo permitido.
            ErrorServicioNoDisponible: Si el servicio no está disponible.
        """
        try:
            if duracion is None:
                raise ErrorParametroFaltante("duracion")
            if not isinstance(duracion, (int, float)) or duracion <= 0:
                raise ErrorCalculoInconsistente(
                    f"La duración debe ser mayor a 0, se recibió: {duracion}"
                )
            if duracion < self.__duracion_minima:
                raise ErrorCalculoInconsistente(
                    f"La duración mínima para este servicio es "
                    f"{self.__duracion_minima}h, se solicitó {duracion}h"
                )
            if not self._disponible:
                raise ErrorServicioNoDisponible(self._nombre)

            multiplicador = self.TARIFAS_NIVEL[self.__nivel]
            costo = self._precio_base * multiplicador * duracion

            urgente = kwargs.get("urgente", False)
            if urgente:
                costo *= 1.20  # Recargo del 20% por urgencia

        except (ErrorParametroFaltante, ErrorCalculoInconsistente,
                ErrorServicioNoDisponible):
            raise
        except Exception as e:
            raise ErrorServicio(
                f"Error inesperado al calcular costo de asesoría: {e}"
            ) from e
        else:
            return round(costo, 2)
        finally:
            pass

    def describir(self) -> str:
        """Retorna descripción completa del servicio de asesoría."""
        multiplicador = self.TARIFAS_NIVEL[self.__nivel]
        precio_real = self._precio_base * multiplicador
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Servicio: Asesoría Especializada\n"
            f"  Nombre            : {self._nombre}\n"
            f"  Área              : {self.__area_especializacion}\n"
            f"  Nivel asesor      : {self.__nivel.capitalize()}\n"
            f"  Precio real/hora  : ${precio_real:,.2f}\n"
            f"  Duración mínima   : {self.__duracion_minima}h\n"
            f"  Estado            : {estado}"
        )

    def validar(self) -> bool:
        """Valida los datos propios de la asesoría además de los del servicio."""
        try:
            super().validar()
            if self.__nivel not in self.NIVELES_VALIDOS:
                raise ErrorServicio(f"Nivel de asesor inválido: {self.__nivel}")
            if self.__duracion_minima <= 0:
                raise ErrorServicio("La duración mínima debe ser mayor a 0")
        except ErrorServicio:
            raise
        except Exception as e:
            raise ErrorServicio(f"Error al validar AsesoriaEspecializada: {e}") from e
        else:
            return True
        finally:
            pass

    def __str__(self) -> str:
        return (
            f"[AsesoriaEspecializada] {self.__area_especializacion} | "
            f"Nivel: {self.__nivel.capitalize()} | "
            f"${self._precio_base:,.2f}/h base"
        )
