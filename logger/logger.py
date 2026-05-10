"""
Módulo del sistema de logs.
Autor: Integrante Lina Alejandra Novoa Aguilar - Responsable de Calidad y Errores
Descripción: Sistema centralizado de registro de eventos y errores
             del sistema Software FJ. Escribe en archivo y en consola.
"""

import logging
import os
from datetime import datetime


class Logger:
    """
    Sistema de logging centralizado para Software FJ.

    Características:
    - Escribe en archivo logs/sistema.log
    - Muestra mensajes en consola simultáneamente
    - Niveles: INFO, WARNING, ERROR, CRITICAL
    - Patrón Singleton: una sola instancia en todo el sistema
    """

    _instancia = None   # Patrón Singleton
    _inicializado = False

    def __new__(cls):
        """Garantiza que solo exista una instancia del logger (Singleton)."""
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    def __init__(self):
        """Configura el logger solo la primera vez que se instancia."""
        if Logger._inicializado:
            return

        Logger._inicializado = True

        # Crear carpeta logs si no existe
        os.makedirs("logs", exist_ok=True)

        # Nombre del archivo de log con fecha
        nombre_archivo = f"logs/sistema.log"

        # Configurar el logger principal
        self._logger = logging.getLogger("SoftwareFJ")
        self._logger.setLevel(logging.DEBUG)

        # Formato de los mensajes
        formato = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Handler para archivo
        manejador_archivo = logging.FileHandler(
            nombre_archivo, encoding="utf-8"
        )
        manejador_archivo.setLevel(logging.DEBUG)
        manejador_archivo.setFormatter(formato)

        # Handler para consola
        manejador_consola = logging.StreamHandler()
        manejador_consola.setLevel(logging.INFO)
        manejador_consola.setFormatter(formato)

        # Agregar handlers al logger
        self._logger.addHandler(manejador_archivo)
        self._logger.addHandler(manejador_consola)

        # Registro inicial
        self._logger.info(" " * 60)
        self._logger.info("Sistema Software FJ iniciado")
        self._logger.info(
            f"Sesión iniciada: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self._logger.info(" " * 60)

    # Métodos de registro

    def info(self, mensaje: str) -> None:
        """Registra un evento informativo."""
        try:
            self._logger.info(mensaje)
        except Exception as e:
            print(f"[Logger] Error al registrar INFO: {e}")

    def warning(self, mensaje: str) -> None:
        """Registra una advertencia."""
        try:
            self._logger.warning(mensaje)
        except Exception as e:
            print(f"[Logger] Error al registrar WARNING: {e}")

    def error(self, mensaje: str) -> None:
        """Registra un error."""
        try:
            self._logger.error(mensaje)
        except Exception as e:
            print(f"[Logger] Error al registrar ERROR: {e}")

    def critico(self, mensaje: str) -> None:
        """Registra un error crítico."""
        try:
            self._logger.critical(mensaje)
        except Exception as e:
            print(f"[Logger] Error al registrar CRITICAL: {e}")

    def registrar_excepcion(self, excepcion: Exception, contexto: str = "") -> None:
        """
        Registra una excepción con su traceback completo.

        Args:
            excepcion (Exception): La excepción capturada.
            contexto  (str):       Descripción de dónde ocurrió.
        """
        try:
            prefijo = f"[{contexto}] " if contexto else ""
            self._logger.error(
                f"{prefijo}{type(excepcion).__name__}: {excepcion}",
                exc_info=True
            )
        except Exception as e:
            print(f"[Logger] Error al registrar excepción: {e}")