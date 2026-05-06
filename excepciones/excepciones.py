"""
Módulo de excepciones personalizadas del sistema Software FJ.
Autor: Integrante Nasly Isabella Velez Muñoz.
Descripción: Define la jerarquía de excepciones propias del sistema,
             permitiendo un manejo de errores preciso y profesional.
"""


class ErrorSistema(Exception):
    """
    Excepción base del sistema Software FJ.
    Todas las excepciones personalizadas heredan de esta clase.
    """
    def __init__(self, mensaje="Error general del sistema Software FJ"):
        self.mensaje = mensaje
        super().__init__(self.mensaje)

    def __str__(self):
        return f"[ErrorSistema] {self.mensaje}"


# Excepciones de validación

class ErrorValidacion(ErrorSistema):
    """Excepción para errores de validación de datos de entrada."""
    def __init__(self, campo: str, detalle: str = "valor no válido"):
        self.campo = campo
        super().__init__(f"Validación fallida en '{campo}': {detalle}")

    def __str__(self):
        return f"[ErrorValidacion] {self.mensaje}"


class ErrorParametroFaltante(ErrorSistema):
    """Excepción cuando falta un parámetro obligatorio."""
    def __init__(self, parametro: str = "desconocido"):
        self.parametro = parametro
        super().__init__(f"Parámetro obligatorio faltante: '{parametro}'")

    def __str__(self):
        return f"[ErrorParametroFaltante] {self.mensaje}"


# Excepciones de cliente

class ErrorCliente(ErrorSistema):
    """Excepción base para errores relacionados con clientes."""
    def __init__(self, mensaje: str = "Error en operación de cliente"):
        super().__init__(mensaje)

    def __str__(self):
        return f"[ErrorCliente] {self.mensaje}"


class ErrorClienteNoEncontrado(ErrorCliente):
    """Excepción cuando un cliente no existe en el sistema."""
    def __init__(self, identificador: str = ""):
        super().__init__(f"Cliente no encontrado con identificador: '{identificador}'")

    def __str__(self):
        return f"[ErrorClienteNoEncontrado] {self.mensaje}"


# Excepciones de servicio

class ErrorServicio(ErrorSistema):
    """Excepción base para errores relacionados con servicios."""
    def __init__(self, mensaje: str = "Error en operación de servicio"):
        super().__init__(mensaje)

    def __str__(self):
        return f"[ErrorServicio] {self.mensaje}"


class ErrorServicioNoDisponible(ErrorServicio):
    """Excepción cuando un servicio no está disponible para reservar."""
    def __init__(self, nombre_servicio: str = ""):
        super().__init__(f"El servicio '{nombre_servicio}' no está disponible actualmente")

    def __str__(self):
        return f"[ErrorServicioNoDisponible] {self.mensaje}"


class ErrorCalculoInconsistente(ErrorServicio):
    """Excepción para cálculos de costo que producen resultados inválidos."""
    def __init__(self, detalle: str = "resultado inválido"):
        super().__init__(f"Cálculo inconsistente detectado: {detalle}")

    def __str__(self):
        return f"[ErrorCalculoInconsistente] {self.mensaje}"


# Excepciones de reserva 

class ErrorReserva(ErrorSistema):
    """Excepción base para errores relacionados con reservas."""
    def __init__(self, mensaje: str = "Error en operación de reserva"):
        super().__init__(mensaje)

    def __str__(self):
        return f"[ErrorReserva] {self.mensaje}"


class ErrorReservaInvalida(ErrorReserva):
    """Excepción para intentos de reserva con datos incorrectos."""
    def __init__(self, razon: str = "datos insuficientes"):
        super().__init__(f"Reserva inválida: {razon}")

    def __str__(self):
        return f"[ErrorReservaInvalida] {self.mensaje}"


class ErrorOperacionNoPermitida(ErrorReserva):
    """Excepción para operaciones no permitidas sobre una reserva."""
    def __init__(self, operacion: str = "", razon: str = "estado incorrecto"):
        super().__init__(f"Operación no permitida '{operacion}': {razon}")

    def __str__(self):
        return f"[ErrorOperacionNoPermitida] {self.mensaje}"