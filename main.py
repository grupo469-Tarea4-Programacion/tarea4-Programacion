"""
Archivo principal del sistema Software FJ.
Autor: Integrante Nasly Isabella Velez Muñoz - Integrador
Descripción: Simula mínimo 10 operaciones completas del sistema,
             incluyendo registros válidos e inválidos de clientes,
             creación correcta e incorrecta de servicios, y reservas
             exitosas y fallidas. Lanza la interfaz gráfica con Tkinter.
"""

from logger.logger import Logger
from clases.cliente import Cliente
from clases.reserva import Reserva
from clases.servicios.reserva_sala import ReservaSala
from clases.servicios.alquiler_equipos import AlquilerEquipos
from clases.servicios.asesoria_especializada import AsesoriaEspecializada
from excepciones.excepciones import (
    ErrorSistema,
    ErrorValidacion,
    ErrorParametroFaltante,
    ErrorCliente,
    ErrorServicio,
    ErrorReserva,
    ErrorOperacionNoPermitida,
    ErrorCalculoInconsistente,
    ErrorServicioNoDisponible,
)
from interfaz import InterfazSoftwareFJ

# Logger global 
logger = Logger()


def separador(titulo: str) -> None:
    """Imprime un separador visual para organizar la salida en consola."""
    print(f"\n{' '*60}")
    print(f"  {titulo}")
    print(f"{' '*60}")


#  OPERACIONES SIMULADAS

def ejecutar_operaciones():
    """
    Ejecuta las 10+ operaciones simuladas del sistema.
    Incluye casos válidos e inválidos para demostrar el manejo
    robusto de excepciones.
    """

    clientes = {}
    servicios = {}

    # OPERACIÓN 1: Registro válido de cliente
    separador("OP 1 — Registro válido de cliente")
    try:
        c1 = Cliente(
            nombre="Ana María Torres",
            documento="1023456789",
            correo="ana.torres@email.com",
            telefono="3101234567"
        )
        clientes["ana"] = c1
        print(f"Cliente creado: {c1}")
        logger.info(f"OP1: Cliente creado exitosamente -> {c1.nombre}")
    except ErrorSistema as e:
        print(f"Error: {e}")
        logger.error(f"OP1: {e}")

    # OPERACIÓN 2: Registro inválido de cliente (correo malo) 
    separador("OP 2 — Registro inválido de cliente (correo inválido)")
    try:
        c2 = Cliente(
            nombre="Luis Pérez",
            documento="987654321",
            correo="correo-sin-arroba",
            telefono="3209876543"
        )
    except ErrorValidacion as e:
        print(f"Validación fallida (esperada): {e}")
        logger.error(f"OP2: {e}")
    except ErrorSistema as e:
        print(f"Error: {e}")
        logger.error(f"OP2: {e}")

    # OPERACIÓN 3: Registro inválido (parámetro faltante) 
    separador("OP 3 — Registro inválido de cliente (documento vacío)")
    try:
        c3 = Cliente(
            nombre="Carlos Ruiz",
            documento="",
            correo="carlos@email.com",
            telefono="3154567890"
        )
    except ErrorValidacion as e:
        print(f"Validación fallida (esperada): {e}")
        logger.error(f"OP3: {e}")
    except ErrorSistema as e:
        print(f"Error: {e}")
        logger.error(f"OP3: {e}")

    # OPERACIÓN 4: Segundo cliente válido
    separador("OP 4 — Registro válido de segundo cliente")
    try:
        c4 = Cliente(
            nombre="Jorge Ramírez",
            documento="1098765432",
            correo="jorge.ramirez@email.com",
            telefono="+573001234567"
        )
        clientes["jorge"] = c4
        print(f"Cliente creado: {c4}")
        logger.info(f"OP4: Cliente creado exitosamente -> {c4.nombre}")
    except ErrorSistema as e:
        print(f"Error: {e}")
        logger.error(f"OP4: {e}")

    # OPERACIÓN 5: Creación válida de servicios 
    separador("OP 5 — Creación válida de tres servicios")
    try:
        sala = ReservaSala(
            nombre="Sala Innovación",
            precio_base=80_000,
            capacidad_maxima=10,
            tiene_proyector=True
        )
        servicios["sala"] = sala
        print(f"{sala}")

        equipo = AlquilerEquipos(
            nombre="Alquiler Portátiles",
            precio_base=25_000,
            tipo_equipo="Portátil Dell Inspiron",
            unidades_disponibles=5,
            requiere_deposito=True
        )
        servicios["equipo"] = equipo
        print(f"{equipo}")

        asesoria = AsesoriaEspecializada(
            nombre="Asesoría Ciberseguridad",
            precio_base=120_000,
            area_especializacion="Ciberseguridad",
            nivel="senior",
            duracion_minima=2.0
        )
        servicios["asesoria"] = asesoria
        print(f"{asesoria}")

        logger.info("OP5: Tres servicios creados exitosamente")

    except ErrorServicio as e:
        print(f"Error en servicio: {e}")
        logger.error(f"OP5: {e}")

    # OPERACIÓN 6: Creación inválida de servicio 
    separador("OP 6 — Creación inválida de servicio (nivel incorrecto)")
    try:
        mal_servicio = AsesoriaEspecializada(
            nombre="Asesoría Redes",
            precio_base=100_000,
            area_especializacion="Redes",
            nivel="maestro"      # Nivel no válido
        )
    except ErrorServicio as e:
        print(f"Error en servicio (esperado): {e}")
        logger.error(f"OP6: {e}")

    # OPERACIÓN 7: Reserva exitosa y confirmada
    separador("OP 7 — Reserva exitosa (sala con proyector)")
    try:
        if "ana" in clientes and "sala" in servicios:
            r1 = Reserva(
                cliente=clientes["ana"],
                servicio=servicios["sala"],
                duracion=3.0,
                num_personas=8
            )
            print(f"{r1}")
            resultado = r1.confirmar()
            print(f"   {resultado}")
            resultado2 = r1.procesar()
            print(f"   {resultado2}")
    except ErrorReserva as e:
        print(f"Error en reserva: {e}")
        logger.error(f"OP7: {e}")

    # OPERACIÓN 8: Reserva con alquiler de equipos 
    separador("OP 8 — Reserva válida de equipos con depósito")
    try:
        if "jorge" in clientes and "equipo" in servicios:
            r2 = Reserva(
                cliente=clientes["jorge"],
                servicio=servicios["equipo"],
                duracion=4.0,
                cantidad=2
            )
            print(f"{r2}")
            deposito = servicios["equipo"].calcular_deposito(4.0, cantidad=2)
            print(f"Depósito requerido: ${deposito:,.2f}")
            resultado = r2.confirmar()
            print(f"   {resultado}")
    except ErrorReserva as e:
        print(f"Error en reserva: {e}")
        logger.error(f"OP8: {e}")

    # OPERACIÓN 9: Reserva fallida (operación no permitida)
    separador("OP 9 — Reserva fallida (cancelar una ya procesada)")
    try:
        if "ana" in clientes and "sala" in servicios:
            # Creamos otra sala disponible para este test
            sala2 = ReservaSala(
                nombre="Sala Creatividad",
                precio_base=60_000,
                capacidad_maxima=6
            )
            r3 = Reserva(
                cliente=clientes["ana"],
                servicio=sala2,
                duracion=2.0
            )
            r3.confirmar()
            r3.procesar()
            # Intentar cancelar una reserva ya procesada -> debe fallar
            r3.cancelar("Ya no se necesita")
    except ErrorOperacionNoPermitida as e:
        print(f"Operación no permitida (esperada): {e}")
        logger.error(f"OP9: {e}")
    except ErrorReserva as e:
        print(f"Error: {e}")
        logger.error(f"OP9: {e}")

    # OPERACIÓN 10: Reserva de asesoría con duración inválida
    separador("OP 10 — Reserva fallida (duración menor al mínimo)")
    try:
        if "jorge" in clientes and "asesoria" in servicios:
            r4 = Reserva(
                cliente=clientes["jorge"],
                servicio=servicios["asesoria"],
                duracion=0.5     # Mínimo es 2.0h -> debe fallar al confirmar
            )
            r4.confirmar()
    except ErrorCalculoInconsistente as e:
        print(f"Cálculo inconsistente (esperado): {e}")
        logger.error(f"OP10: {e}")
    except ErrorReserva as e:
        print(f"Error: {e}")
        logger.error(f"OP10: {e}")

    # OPERACIÓN 11: Costo con impuesto y descuento
    separador("OP 11 — Métodos sobrecargados de cálculo de costo")
    try:
        if "sala" in servicios:
            sala = servicios["sala"]
            costo_base = sala.calcular_costo(2.0, num_personas=5)
            costo_iva = sala.calcular_costo_con_impuesto(2.0)
            costo_desc = sala.calcular_costo_con_descuento(
                2.0, descuento=0.10, aplicar_impuesto=True
            )
            print(f"Sala Innovación — 2 horas:")
            print(f"   Costo base              : ${costo_base:,.2f}")
            print(f"   Con IVA (19%)           : ${costo_iva:,.2f}")
            print(f"   Con 10% descuento + IVA : ${costo_desc:,.2f}")
            logger.info(
                f"OP11: Cálculos sobrecargados -> "
                f"base=${costo_base}, IVA=${costo_iva}, "
                f"desc+IVA=${costo_desc}"
            )
    except ErrorSistema as e:
        print(f"Error: {e}")
        logger.error(f"OP11: {e}")

    # OPERACIÓN 12: Cancelación válida de reserva
    separador("OP 12 — Cancelación válida de reserva pendiente")
    try:
        if "ana" in clientes and "equipo" in servicios:
            r5 = Reserva(
                cliente=clientes["ana"],
                servicio=servicios["equipo"],
                duracion=1.0,
                cantidad=1
            )
            print(f"{r5}")
            resultado = r5.cancelar("El cliente cambió de planes")
            print(f"   {resultado}")
    except ErrorReserva as e:
        print(f"Error: {e}")
        logger.error(f"OP12: {e}")

    separador("SIMULACIÓN COMPLETADA — Iniciando interfaz gráfica")
    logger.info("Simulación de operaciones completada. Iniciando GUI.")


#  PUNTO DE ENTRADA

if __name__ == "__main__":
    ejecutar_operaciones()
    app = InterfazSoftwareFJ()
    app.mainloop()