"""
Módulo con la clase abstracta base Entidad.
Autor: Integrante Nasly Isabella Velez Muñoz.
Descripción: Define la estructura común de todas las entidades
             del sistema (clientes, servicios, reservas).
"""

from abc import ABC, abstractmethod
from datetime import datetime


class Entidad(ABC):
    """
    Clase abstracta base para todas las entidades del sistema Software FJ.

    Implementa:
    - Abstracción: métodos abstractos describir() y validar()
    - Encapsulación: atributos protegidos con propiedades
    - Identificador único automático por clase
    """

    _contador_global: int = 0  # Contador compartido entre todas las entidades

    def __init__(self, nombre: str):
        """
        Inicializa una entidad con nombre y genera su ID automáticamente.

        Args:
            nombre (str): Nombre descriptivo de la entidad.
        """
        Entidad._contador_global += 1
        self._id: int = Entidad._contador_global
        self._nombre: str = nombre
        self._fecha_creacion: datetime = datetime.now()

    # Propiedades (encapsulación) 

    @property
    def id(self) -> int:
        """Identificador único de la entidad (solo lectura)."""
        return self._id

    @property
    def nombre(self) -> str:
        """Nombre de la entidad."""
        return self._nombre

    @property
    def fecha_creacion(self) -> datetime:
        """Fecha y hora en que se creó la entidad (solo lectura)."""
        return self._fecha_creacion

    # Métodos abstractos 

    @abstractmethod
    def describir(self) -> str:
        """
        Retorna una descripción detallada de la entidad.
        Debe ser implementado por cada subclase.
        """
        pass

    @abstractmethod
    def validar(self) -> bool:
        """
        Valida que los datos de la entidad sean correctos y completos.
        Debe ser implementado por cada subclase.
        Retorna True si es válida, lanza excepción si no lo es.
        """
        pass

    # Métodos concretos

    def obtener_info_base(self) -> str:
        """Retorna información básica común a todas las entidades."""
        fecha_str = self._fecha_creacion.strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"ID: {self._id} | "
            f"Nombre: {self._nombre} | "
            f"Creado: {fecha_str}"
        )

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}] {self.obtener_info_base()}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self._id}, "
            f"nombre='{self._nombre}')"
        )
    