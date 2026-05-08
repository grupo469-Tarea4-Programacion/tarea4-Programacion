# Software FJ - Sistema Integral de Gestion de Clientes, Servicios y Reservas

Proyecto academico - Programacion Orientada a Objetos
Universidad Nacional Abierta y a Distancia (UNAD)
Curso: Programacion | Codigo: 213023


## Descripcion General

Software FJ es un sistema integral orientado a objetos desarrollado en
Python, capaz de gestionar clientes, servicios y reservas sin el uso de
bases de datos. Toda la informacion se maneja mediante objetos, listas en
memoria y archivos de log para el registro de eventos y errores.

El sistema ofrece tres tipos de servicios:
- Reserva de salas de reuniones
- Alquiler de equipos tecnologicos
- Asesorias especializadas


## Equipo de Desarrollo

| Integrante       | Rol                              | Rama Git                  |
|------------------|----------------------------------|---------------------------|
| Integrante Nasly | Arquitecto del Sistema           | estructura_sistema        |
| Integrante Lina  | Desarrollador de Clientes        | desarrollador_clientes    |
| Integrante Nasly | Desarrollador de Servicios       | desarrollador_servicios   |
| Integrante Lina  | Responsable de Calidad y Errores | calidad_errores           |
| Integrante Nasly | Integrador                       | integrador                |


## Estructura del Proyecto

SoftwareFJ/
├── clases/
│   ├── __init__.py
│   ├── entidad.py                    # Clase abstracta base del sistema
│   ├── servicio.py                   # Clase abstracta Servicio
│   ├── cliente.py                    # Clase Cliente con encapsulacion
│   ├── reserva.py                    # Clase Reserva con flujo completo
│   └── servicios/
│       ├── __init__.py
│       ├── reserva_sala.py           # Servicio: Reserva de Sala
│       ├── alquiler_equipos.py       # Servicio: Alquiler de Equipos
│       └── asesoria_especializada.py # Servicio: Asesoria Especializada
├── excepciones/
│   ├── __init__.py
│   └── excepciones.py               # Jerarquia de excepciones personalizadas
├── logger/
│   ├── __init__.py
│   └── logger.py                    # Sistema centralizado de logs (Singleton)
├── logs/
│   └── sistema.log                  # Archivo generado en tiempo de ejecucion
├── interfaz.py                      # Interfaz grafica con Tkinter
├── main.py                          # Punto de entrada y simulacion de operaciones
├── .gitignore
└── README.md


## Principios de POO Aplicados

### Abstraccion
- Entidad: clase abstracta base con metodos describir() y validar()
- Servicio: clase abstracta con metodos calcular_costo() y describir()

### Herencia

Entidad (abstracta)
  ├── Cliente
  └── Servicio (abstracta)
        ├── ReservaSala
        ├── AlquilerEquipos
        └── AsesoriaEspecializada

### Polimorfismo
Cada servicio implementa su propia version de calcular_costo() y
describir(), con comportamientos distintos segun el tipo de servicio.

### Encapsulacion
- Cliente: atributos privados con doble guion bajo (__documento,
  __correo, __telefono) accesibles solo mediante propiedades y setters
  con validacion.
- Reserva: estado interno protegido, modificable unicamente a traves de
  los metodos confirmar(), cancelar() y procesar().

### Metodos Sobrecargados
La clase Servicio expone tres variantes del calculo de costo:
- calcular_costo(duracion)                              costo base
- calcular_costo_con_impuesto(duracion, impuesto)       con IVA
- calcular_costo_con_descuento(duracion, descuento, aplicar_impuesto)


## Manejo de Excepciones

### Jerarquia de Excepciones Personalizadas

ErrorSistema
  ├── ErrorValidacion
  ├── ErrorParametroFaltante
  ├── ErrorCliente
  │     └── ErrorClienteNoEncontrado
  ├── ErrorServicio
  │     ├── ErrorServicioNoDisponible
  │     └── ErrorCalculoInconsistente
  └── ErrorReserva
        ├── ErrorReservaInvalida
        └── ErrorOperacionNoPermitida

### Bloques Utilizados

| Bloque                      | Donde se usa                               |
|-----------------------------|--------------------------------------------|
| try/except                  | Validaciones de cliente, servicio, reserva |
| try/except/else             | Calculo de costos, confirmacion de reservas|
| try/except/finally          | Validaciones con cierre garantizado        |
| Encadenamiento (raise from) | Re-lanzamiento con causa original          |


## Estados de una Reserva

PENDIENTE  -->  CONFIRMADA  -->  PROCESADA
    |
    +-----------------------------> CANCELADA

- Solo se puede confirmar desde el estado pendiente
- Solo se puede procesar desde el estado confirmada
- Solo se puede cancelar desde pendiente o confirmada


## Instalacion y Ejecucion

### Requisitos
- Python 3.10 o superior
- Tkinter (incluido en la instalacion estandar de Python)
- No requiere librerias externas

### Pasos

# 1. Clonar el repositorio
git clone https://github.com/grupo469-Tarea4-Programacion/tarea4-Programacion.git 

# 2. Entrar a la carpeta
cd SoftwareFJ

# 3. Ejecutar el sistema
python main.py

Al ejecutar main.py:
1. Se corren automaticamente 12 operaciones simuladas en consola
2. Se genera el archivo logs/sistema.log con todos los eventos
3. Se abre la interfaz grafica con Tkinter


## Interfaz Grafica

La ventana principal esta organizada en cuatro pestanas:
 _____________________________________________________________________
| Pestana   | Funcionalidad                                           |
|-----------|---------------------------------------------------------|
| Clientes  | Registrar clientes con validacion en tiempo real        |
| Servicios | Crear los tres tipos de servicios disponibles           |
| Reservas  | Crear, confirmar, procesar y cancelar reservas          |
| Logs      | Visualizar el contenido del archivo sistema.log         |


## Operaciones Simuladas en main.py
 _______________________________________________________________________________
| N  | Operacion                                  | Resultado Esperado          |
|----|--------------------------------------------|-----------------------------|
| 1  | Registro valido de cliente                 | Exito                       |
| 2  | Cliente con correo invalido                | ErrorValidacion             |
| 3  | Cliente con documento vacio                | ErrorValidacion             |
| 4  | Segundo cliente valido                     | Exito                       |
| 5  | Creacion de tres servicios                 | Exito                       |
| 6  | Servicio con nivel invalido                | ErrorServicio               |
| 7  | Reserva de sala confirmada y procesada     | Exito                       |
| 8  | Reserva de equipos con deposito            | Exito                       |
| 9  | Cancelar reserva ya procesada              | ErrorOperacionNoPermitida   |
| 10 | Asesoria con duracion menor al minimo      | ErrorCalculoInconsistente   |
| 11 | Calculos con impuesto y descuento          | Exito                       |
| 12 | Cancelacion valida de reserva pendiente    | Exito                       |


## Sistema de Logs

El sistema registra automaticamente todos los eventos en
logs/sistema.log con el siguiente formato:

2025-01-15 10:30:00 | INFO     | Sistema Software FJ iniciado
2025-01-15 10:30:00 | INFO     | OP1: Cliente creado exitosamente -> Ana Maria Torres
2025-01-15 10:30:00 | ERROR    | OP2: [ErrorValidacion] correo: valor no valido

El logger implementa el patron Singleton, garantizando una unica
instancia activa durante toda la ejecucion del sistema.


## Flujo de Trabajo en Git

Cada integrante trabajo en sus propias ramas y realizo Pull Request hacia
main al completar su parte:

main
  ├── estructura_sistema       PR #1 mergeado
  ├── desarrollador_clientes   PR #2 mergeado
  ├── desarrollador_servicios  PR #3 mergeado
  ├── calidad_errores          PR #4 mergeado
  └── integrador               PR #5 mergeado


## Licencia

Proyecto academico desarrollado para el curso de Programacion (213023)
de la Universidad Nacional Abierta y a Distancia - UNAD.