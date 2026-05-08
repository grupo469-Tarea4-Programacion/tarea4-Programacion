"""
Módulo de interfaz gráfica con Tkinter.
Autor: Integrante Nasly Isabella Velez Muñoz - Integrador
Descripción: Interfaz gráfica que conecta todas las funcionalidades
             del sistema Software FJ: gestión de clientes, servicios
             y reservas.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from logger.logger import Logger
from clases.cliente import Cliente
from clases.reserva import Reserva
from clases.servicios.reserva_sala import ReservaSala
from clases.servicios.alquiler_equipos import AlquilerEquipos
from clases.servicios.asesoria_especializada import AsesoriaEspecializada
from excepciones.excepciones import ErrorSistema


class InterfazSoftwareFJ(tk.Tk):
    """
    Ventana principal de la aplicación Software FJ.
    Organizada en pestañas: Clientes, Servicios, Reservas, Logs.
    """

    COLOR_FONDO    = "#1e1e2e"
    COLOR_PANEL    = "#2a2a3e"
    COLOR_ACENTO   = "#7c3aed"
    COLOR_TEXTO    = "#e2e8f0"
    COLOR_EXITO    = "#22c55e"
    COLOR_ERROR    = "#ef4444"
    COLOR_ENTRADA  = "#3b3b52"

    def __init__(self):
        super().__init__()

        self.logger = Logger()

        # Datos en memoria
        self._clientes: list[Cliente] = []
        self._servicios: list = []
        self._reservas: list[Reserva] = []

        self._configurar_ventana()
        self._construir_ui()

    # Configuración de la ventana 

    def _configurar_ventana(self) -> None:
        self.title("Software FJ Sistema de Gestión")
        self.geometry("900x650")
        self.resizable(True, True)
        self.configure(bg=self.COLOR_FONDO)

        # Estilo general
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(
            "TNotebook",
            background=self.COLOR_FONDO,
            borderwidth=0
        )
        estilo.configure(
            "TNotebook.Tab",
            background=self.COLOR_PANEL,
            foreground=self.COLOR_TEXTO,
            padding=[16, 8],
            font=("Segoe UI", 10, "bold")
        )
        estilo.map(
            "TNotebook.Tab",
            background=[("selected", self.COLOR_ACENTO)],
            foreground=[("selected", "white")]
        )
        estilo.configure(
            "TFrame", background=self.COLOR_FONDO
        )

    # Construcción de la UI

    def _construir_ui(self) -> None:
        """Construye el encabezado y las pestañas principales."""

        # Encabezado
        encabezado = tk.Frame(self, bg=self.COLOR_ACENTO, height=55)
        encabezado.pack(fill="x")
        tk.Label(
            encabezado,
            text=" Software FJ Sistema Integral de Gestión",
            font=("Segoe UI", 14, "bold"),
            bg=self.COLOR_ACENTO,
            fg="white",
            pady=12
        ).pack()

        # Notebook (pestañas)
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self._tab_clientes(nb)
        self._tab_servicios(nb)
        self._tab_reservas(nb)
        self._tab_logs(nb)

    #  PESTAÑA 1 — CLIENTES

    def _tab_clientes(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb)
        nb.add(frame, text=" Clientes")
        frame.configure(style="TFrame")

        # Formulario 
        form = tk.LabelFrame(
            frame, text=" Registrar Cliente ",
            bg=self.COLOR_PANEL, fg=self.COLOR_ACENTO,
            font=("Segoe UI", 10, "bold"), bd=2
        )
        form.pack(fill="x", padx=15, pady=(15, 5))

        campos = [
            ("Nombre completo:", "entry_nombre_cli"),
            ("Documento (cédula):", "entry_doc_cli"),
            ("Correo electrónico:", "entry_correo_cli"),
            ("Teléfono:", "entry_tel_cli"),
        ]

        for i, (label, attr) in enumerate(campos):
            tk.Label(
                form, text=label,
                bg=self.COLOR_PANEL, fg=self.COLOR_TEXTO,
                font=("Segoe UI", 9)
            ).grid(row=i, column=0, sticky="w", padx=12, pady=6)

            entrada = tk.Entry(
                form, width=38,
                bg=self.COLOR_ENTRADA, fg=self.COLOR_TEXTO,
                insertbackground=self.COLOR_TEXTO,
                relief="flat", font=("Segoe UI", 9)
            )
            entrada.grid(row=i, column=1, padx=12, pady=6)
            setattr(self, attr, entrada)

        tk.Button(
            form, text=" Registrar Cliente",
            bg=self.COLOR_ACENTO, fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=10,
            command=self._registrar_cliente
        ).grid(row=len(campos), column=0, columnspan=2, pady=10)

        # Lista de clientes
        lista_frame = tk.LabelFrame(
            frame, text=" Clientes Registrados ",
            bg=self.COLOR_PANEL, fg=self.COLOR_ACENTO,
            font=("Segoe UI", 10, "bold"), bd=2
        )
        lista_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.lista_clientes = tk.Listbox(
            lista_frame,
            bg=self.COLOR_ENTRADA, fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9), relief="flat",
            selectbackground=self.COLOR_ACENTO
        )
        self.lista_clientes.pack(
            fill="both", expand=True, padx=8, pady=8
        )

    def _registrar_cliente(self) -> None:
        """Lee el formulario y crea un Cliente."""
        try:
            cliente = Cliente(
                nombre=self.entry_nombre_cli.get(),
                documento=self.entry_doc_cli.get(),
                correo=self.entry_correo_cli.get(),
                telefono=self.entry_tel_cli.get(),
            )
            self._clientes.append(cliente)
            self.lista_clientes.insert(
                tk.END,
                f"#{cliente.id}  {cliente.nombre}  |  {cliente.correo}"
            )
            self._limpiar_entradas(
                self.entry_nombre_cli, self.entry_doc_cli,
                self.entry_correo_cli, self.entry_tel_cli
            )
            messagebox.showinfo(
                "Cliente Registrado",
                f"Cliente '{cliente.nombre}' registrado exitosamente."
            )
            self.logger.info(f"GUI: Cliente registrado -> {cliente.nombre}")
            self._actualizar_combos()

        except ErrorSistema as e:
            messagebox.showerror("Error de Validación", str(e))
            self.logger.error(f"GUI: Error al registrar cliente -> {e}")

    #  PESTAÑA 2 — SERVICIOS

    def _tab_servicios(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb)
        nb.add(frame, text="Servicios")

        # Tipo de servicio
        tipo_frame = tk.Frame(frame, bg=self.COLOR_FONDO)
        tipo_frame.pack(fill="x", padx=15, pady=(15, 0))

        tk.Label(
            tipo_frame, text="Tipo de servicio:",
            bg=self.COLOR_FONDO, fg=self.COLOR_TEXTO,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 10))

        self.tipo_servicio = tk.StringVar(value="Sala")
        for tipo in ("Sala", "Equipo", "Asesoría"):
            tk.Radiobutton(
                tipo_frame, text=tipo,
                variable=self.tipo_servicio, value=tipo,
                bg=self.COLOR_FONDO, fg=self.COLOR_TEXTO,
                selectcolor=self.COLOR_PANEL,
                activebackground=self.COLOR_FONDO,
                font=("Segoe UI", 9),
                command=self._mostrar_campos_servicio
            ).pack(side="left", padx=6)

        # Campos dinámicos
        self.form_serv = tk.LabelFrame(
            frame, text=" Datos del Servicio ",
            bg=self.COLOR_PANEL, fg=self.COLOR_ACENTO,
            font=("Segoe UI", 10, "bold"), bd=2
        )
        self.form_serv.pack(fill="x", padx=15, pady=8)
        self._mostrar_campos_servicio()

        # Lista
        lista_frame = tk.LabelFrame(
            frame, text=" Servicios Creados ",
            bg=self.COLOR_PANEL, fg=self.COLOR_ACENTO,
            font=("Segoe UI", 10, "bold"), bd=2
        )
        lista_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.lista_servicios = tk.Listbox(
            lista_frame,
            bg=self.COLOR_ENTRADA, fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9), relief="flat",
            selectbackground=self.COLOR_ACENTO
        )
        self.lista_servicios.pack(
            fill="both", expand=True, padx=8, pady=8
        )

    def _lbl_entry(self, parent, texto, row, attr) -> tk.Entry:
        """Crea un par label+entry dentro de un frame."""
        tk.Label(
            parent, text=texto,
            bg=self.COLOR_PANEL, fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9)
        ).grid(row=row, column=0, sticky="w", padx=12, pady=5)
        e = tk.Entry(
            parent, width=34,
            bg=self.COLOR_ENTRADA, fg=self.COLOR_TEXTO,
            insertbackground=self.COLOR_TEXTO,
            relief="flat", font=("Segoe UI", 9)
        )
        e.grid(row=row, column=1, padx=12, pady=5)
        setattr(self, attr, e)
        return e

    def _mostrar_campos_servicio(self) -> None:
        """Destruye y reconstruye los campos según el tipo elegido."""
        for w in self.form_serv.winfo_children():
            w.destroy()

        tipo = self.tipo_servicio.get()
        self._lbl_entry(self.form_serv, "Nombre del servicio:", 0, "sv_nombre")
        self._lbl_entry(self.form_serv, "Precio base por hora ($):", 1, "sv_precio")

        if tipo == "Sala":
            self._lbl_entry(self.form_serv, "Capacidad máxima (personas):", 2, "sv_cap")
            tk.Label(
                self.form_serv, text="¿Tiene proyector?",
                bg=self.COLOR_PANEL, fg=self.COLOR_TEXTO,
                font=("Segoe UI", 9)
            ).grid(row=3, column=0, sticky="w", padx=12, pady=5)
            self.sv_proyector = tk.BooleanVar()
            tk.Checkbutton(
                self.form_serv, variable=self.sv_proyector,
                bg=self.COLOR_PANEL, activebackground=self.COLOR_PANEL
            ).grid(row=3, column=1, sticky="w", padx=12)

        elif tipo == "Equipo":
            self._lbl_entry(self.form_serv, "Tipo de equipo:", 2, "sv_tipo_eq")
            self._lbl_entry(self.form_serv, "Unidades disponibles:", 3, "sv_unidades")

        elif tipo == "Asesoría":
            self._lbl_entry(self.form_serv, "Área de especialización:", 2, "sv_area")
            tk.Label(
                self.form_serv, text="Nivel del asesor:",
                bg=self.COLOR_PANEL, fg=self.COLOR_TEXTO,
                font=("Segoe UI", 9)
            ).grid(row=3, column=0, sticky="w", padx=12, pady=5)
            self.sv_nivel = ttk.Combobox(
                self.form_serv,
                values=["junior", "senior", "experto"],
                state="readonly", width=15,
                font=("Segoe UI", 9)
            )
            self.sv_nivel.set("junior")
            self.sv_nivel.grid(row=3, column=1, sticky="w", padx=12)
            self._lbl_entry(self.form_serv, "Duración mínima (horas):", 4, "sv_dur_min")

        tk.Button(
            self.form_serv, text=" Crear Servicio",
            bg=self.COLOR_ACENTO, fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=10,
            command=self._crear_servicio
        ).grid(row=10, column=0, columnspan=2, pady=10)

    def _crear_servicio(self) -> None:
        """Lee el formulario y crea el servicio correspondiente."""
        try:
            tipo = self.tipo_servicio.get()
            nombre = self.sv_nombre.get()
            precio = float(self.sv_precio.get())

            if tipo == "Sala":
                servicio = ReservaSala(
                    nombre=nombre,
                    precio_base=precio,
                    capacidad_maxima=int(self.sv_cap.get()),
                    tiene_proyector=self.sv_proyector.get()
                )
            elif tipo == "Equipo":
                servicio = AlquilerEquipos(
                    nombre=nombre,
                    precio_base=precio,
                    tipo_equipo=self.sv_tipo_eq.get(),
                    unidades_disponibles=int(self.sv_unidades.get())
                )
            else:
                servicio = AsesoriaEspecializada(
                    nombre=nombre,
                    precio_base=precio,
                    area_especializacion=self.sv_area.get(),
                    nivel=self.sv_nivel.get(),
                    duracion_minima=float(self.sv_dur_min.get())
                )

            self._servicios.append(servicio)
            self.lista_servicios.insert(
                tk.END,
                f"#{servicio.id}  [{tipo}]  {nombre}  |  "
                f"${precio:,.0f}/h"
            )
            messagebox.showinfo(
                "Servicio Creado",
                f" Servicio '{nombre}' creado exitosamente."
            )
            self.logger.info(f"GUI: Servicio creado -> {nombre}")
            self._actualizar_combos()

        except ErrorSistema as e:
            messagebox.showerror("Error en Servicio", str(e))
            self.logger.error(f"GUI: Error al crear servicio -> {e}")
        except ValueError as e:
            messagebox.showerror(
                "Error de Formato",
                f"Verifica que precio/capacidad sean números.\n{e}"
            )

    #  PESTAÑA 3 — RESERVAS

    def _tab_reservas(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb)
        nb.add(frame, text=" Reservas")

        form = tk.LabelFrame(
            frame, text=" Nueva Reserva ",
            bg=self.COLOR_PANEL, fg=self.COLOR_ACENTO,
            font=("Segoe UI", 10, "bold"), bd=2
        )
        form.pack(fill="x", padx=15, pady=15)

        # Cliente
        tk.Label(
            form, text="Cliente:",
            bg=self.COLOR_PANEL, fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9)
        ).grid(row=0, column=0, sticky="w", padx=12, pady=6)
        self.combo_cliente = ttk.Combobox(
            form, state="readonly", width=35,
            font=("Segoe UI", 9)
        )
        self.combo_cliente.grid(row=0, column=1, padx=12, pady=6)

        # Servicio
        tk.Label(
            form, text="Servicio:",
            bg=self.COLOR_PANEL, fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9)
        ).grid(row=1, column=0, sticky="w", padx=12, pady=6)
        self.combo_servicio = ttk.Combobox(
            form, state="readonly", width=35,
            font=("Segoe UI", 9)
        )
        self.combo_servicio.grid(row=1, column=1, padx=12, pady=6)

        # Duración
        tk.Label(
            form, text="Duración (horas):",
            bg=self.COLOR_PANEL, fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9)
        ).grid(row=2, column=0, sticky="w", padx=12, pady=6)
        self.entry_duracion = tk.Entry(
            form, width=15,
            bg=self.COLOR_ENTRADA, fg=self.COLOR_TEXTO,
            insertbackground=self.COLOR_TEXTO,
            relief="flat", font=("Segoe UI", 9)
        )
        self.entry_duracion.grid(row=2, column=1, sticky="w", padx=12)

        # Botones
        btn_frame = tk.Frame(form, bg=self.COLOR_PANEL)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        for texto, cmd, color in [
            (" Crear Reserva",    self._crear_reserva,     self.COLOR_ACENTO),
            (" Confirmar",       self._confirmar_reserva,  "#16a34a"),
            (" Procesar",        self._procesar_reserva,   "#0284c7"),
            (" Cancelar",       self._cancelar_reserva,   "#dc2626"),
        ]:
            tk.Button(
                btn_frame, text=texto,
                bg=color, fg="white",
                font=("Segoe UI", 9, "bold"),
                relief="flat", cursor="hand2", padx=8, pady=4,
                command=cmd
            ).pack(side="left", padx=5)

        # Lista de reservas
        lista_frame = tk.LabelFrame(
            frame, text=" Reservas del Sistema ",
            bg=self.COLOR_PANEL, fg=self.COLOR_ACENTO,
            font=("Segoe UI", 10, "bold"), bd=2
        )
        lista_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.lista_reservas = tk.Listbox(
            lista_frame,
            bg=self.COLOR_ENTRADA, fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9), relief="flat",
            selectbackground=self.COLOR_ACENTO
        )
        self.lista_reservas.pack(
            fill="both", expand=True, padx=8, pady=8
        )

    def _crear_reserva(self) -> None:
        try:
            idx_cli = self.combo_cliente.current()
            idx_srv = self.combo_servicio.current()
            if idx_cli < 0 or idx_srv < 0:
                messagebox.showwarning(
                    "Datos faltantes", "Selecciona un cliente y un servicio."
                )
                return
            duracion = float(self.entry_duracion.get())
            cliente = self._clientes[idx_cli]
            servicio = self._servicios[idx_srv]

            reserva = Reserva(
                cliente=cliente,
                servicio=servicio,
                duracion=duracion
            )
            self._reservas.append(reserva)
            self._actualizar_lista_reservas()
            messagebox.showinfo(
                "Reserva Creada", f"{reserva}"
            )
            self.logger.info(f"GUI: Reserva creada -> {reserva}")

        except ErrorSistema as e:
            messagebox.showerror("Error en Reserva", str(e))
            self.logger.error(f"GUI: Error al crear reserva -> {e}")
        except ValueError:
            messagebox.showerror(
                "Error de Formato", "La duración debe ser un número."
            )

    def _reserva_seleccionada(self):
        sel = self.lista_reservas.curselection()
        if not sel:
            messagebox.showwarning("Sin selección", "Selecciona una reserva.")
            return None
        return self._reservas[sel[0]]

    def _confirmar_reserva(self) -> None:
        reserva = self._reserva_seleccionada()
        if not reserva:
            return
        try:
            msg = reserva.confirmar()
            self._actualizar_lista_reservas()
            messagebox.showinfo("Confirmada", msg)
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e))
            self.logger.error(f"GUI: Error al confirmar -> {e}")

    def _procesar_reserva(self) -> None:
        reserva = self._reserva_seleccionada()
        if not reserva:
            return
        try:
            msg = reserva.procesar()
            self._actualizar_lista_reservas()
            messagebox.showinfo("Procesada", msg)
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e))
            self.logger.error(f"GUI: Error al procesar -> {e}")

    def _cancelar_reserva(self) -> None:
        reserva = self._reserva_seleccionada()
        if not reserva:
            return
        try:
            msg = reserva.cancelar("Cancelado desde la interfaz")
            self._actualizar_lista_reservas()
            messagebox.showinfo("Cancelada", msg)
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e))
            self.logger.error(f"GUI: Error al cancelar -> {e}")

    def _actualizar_lista_reservas(self) -> None:
        self.lista_reservas.delete(0, tk.END)
        for r in self._reservas:
            self.lista_reservas.insert(tk.END, str(r))

    #  PESTAÑA 4 — LOGS

    def _tab_logs(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb)
        nb.add(frame, text=" Logs")

        tk.Label(
            frame,
            text="Contenido del archivo logs/sistema.log",
            bg=self.COLOR_FONDO, fg=self.COLOR_TEXTO,
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(12, 4))

        self.area_logs = scrolledtext.ScrolledText(
            frame,
            bg=self.COLOR_ENTRADA, fg="#86efac",
            font=("Consolas", 9), relief="flat",
            state="disabled"
        )
        self.area_logs.pack(
            fill="both", expand=True, padx=15, pady=(0, 10)
        )

        tk.Button(
            frame, text=" Actualizar Logs",
            bg=self.COLOR_ACENTO, fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", padx=10,
            command=self._cargar_logs
        ).pack(pady=(0, 10))

        self._cargar_logs()

    def _cargar_logs(self) -> None:
        """Lee el archivo de logs y lo muestra en el área de texto."""
        try:
            with open("logs/sistema.log", "r", encoding="utf-8") as f:
                contenido = f.read()
            self.area_logs.configure(state="normal")
            self.area_logs.delete("1.0", tk.END)
            self.area_logs.insert(tk.END, contenido)
            self.area_logs.configure(state="disabled")
            self.area_logs.see(tk.END)
        except FileNotFoundError:
            self.area_logs.configure(state="normal")
            self.area_logs.insert(
                tk.END, "Aún no hay archivo de logs generado.\n"
            )
            self.area_logs.configure(state="disabled")

    # Utilidades

    def _actualizar_combos(self) -> None:
        """Actualiza los combos de clientes y servicios en la pestaña Reservas."""
        self.combo_cliente["values"] = [
            f"#{c.id} {c.nombre}" for c in self._clientes
        ]
        self.combo_servicio["values"] = [
            f"#{s.id} {s.nombre}" for s in self._servicios
        ]

    @staticmethod
    def _limpiar_entradas(*entradas) -> None:
        for e in entradas:
            e.delete(0, tk.END)