"""
Módulo de interfaz gráfica con Tkinter.
Autor: Integrante Nasly Isabella Velez Muñoz - Integrador
Descripción: Interfaz gráfica que conecta todas las funcionalidades
             del sistema Software FJ: gestión de clientes, servicios
             y reservas.
"""

import re
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from logger.logger import Logger
from clases.cliente import Cliente
from clases.reserva import Reserva
from clases.servicios.reserva_sala import ReservaSala
from clases.servicios.alquiler_equipos import AlquilerEquipos
from clases.servicios.asesoria_especializada import AsesoriaEspecializada
from excepciones.excepciones import ErrorSistema, ErrorValidacion


class InterfazSoftwareFJ(tk.Tk):
    """Main application window for Software FJ."""

    COLOR_FONDO = "#1e1e2e"
    COLOR_PANEL = "#2a2a3e"
    COLOR_ACENTO = "#7c3aed"
    COLOR_TEXTO = "#e2e8f0"
    COLOR_EXITO = "#22c55e"
    COLOR_ERROR = "#ef4444"
    COLOR_ENTRADA = "#3b3b52"

    NAME_PATTERN = re.compile(
        r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü]+(?: [A-Za-zÁÉÍÓÚáéíóúÑñÜü]+)*$"
    )
    SIMPLE_TEXT_PATTERN = re.compile(
        r"^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñÜü]+(?:[ A-Za-z0-9ÁÉÍÓÚáéíóúÑñÜü\-]*[A-Za-z0-9ÁÉÍÓÚáéíóúÑñÜü])?$"
    )
    EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}$")
    DECIMAL_PATTERN = re.compile(r"^\d+(?:\.\d+)?$")
    INTEGER_PATTERN = re.compile(r"^\d+$")
    PHONE_PATTERN = re.compile(r"^(?!([0-9])\1+$)\d{10,15}$")

    def __init__(self):
        super().__init__()

        self.logger = Logger()

        # In-memory data
        self._clientes: list[Cliente] = []
        self._servicios: list = []
        self._reservas: list[Reserva] = []

        self._configurar_ventana()
        self._construir_ui()

    # Window configuration

    def _configurar_ventana(self) -> None:
        self.title("Software FJ Management System")
        self.geometry("900x650")
        self.resizable(True, True)
        self.configure(bg=self.COLOR_FONDO)

        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(
            "TNotebook",
            background=self.COLOR_FONDO,
            borderwidth=0,
        )
        estilo.configure(
            "TNotebook.Tab",
            background=self.COLOR_PANEL,
            foreground=self.COLOR_TEXTO,
            padding=[16, 8],
            font=("Segoe UI", 10, "bold"),
        )
        estilo.map(
            "TNotebook.Tab",
            background=[("selected", self.COLOR_ACENTO)],
            foreground=[("selected", "white")],
        )
        estilo.configure("TFrame", background=self.COLOR_FONDO)

    # UI construction

    def _construir_ui(self) -> None:
        header = tk.Frame(self, bg=self.COLOR_ACENTO, height=55)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Software FJ Integrated Management System",
            font=("Segoe UI", 14, "bold"),
            bg=self.COLOR_ACENTO,
            fg="white",
            pady=12,
        ).pack()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self._tab_clientes(nb)
        self._tab_servicios(nb)
        self._tab_reservas(nb)
        self._tab_logs(nb)

    # Tab 1 - Clients

    def _tab_clientes(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb)
        nb.add(frame, text="Clients")
        frame.configure(style="TFrame")

        form = tk.LabelFrame(
            frame,
            text=" Register Client ",
            bg=self.COLOR_PANEL,
            fg=self.COLOR_ACENTO,
            font=("Segoe UI", 10, "bold"),
            bd=2,
        )
        form.pack(fill="x", padx=15, pady=(15, 5))

        campos = [
            ("Full name (letters only, min 3):", "entry_nombre_cli"),
            ("ID number (digits only, 6-15):", "entry_doc_cli"),
            ("Email address (example: correo@gmail.com):", "entry_correo_cli"),
            ("Phone number (digits only, min 10):", "entry_tel_cli"),
        ]

        for i, (label, attr) in enumerate(campos):
            tk.Label(
                form,
                text=label,
                bg=self.COLOR_PANEL,
                fg=self.COLOR_TEXTO,
                font=("Segoe UI", 9),
            ).grid(row=i, column=0, sticky="w", padx=12, pady=6)

            entry = tk.Entry(
                form,
                width=38,
                bg=self.COLOR_ENTRADA,
                fg=self.COLOR_TEXTO,
                insertbackground=self.COLOR_TEXTO,
                relief="flat",
                font=("Segoe UI", 9),
            )
            entry.grid(row=i, column=1, padx=12, pady=6)
            setattr(self, attr, entry)

        tk.Button(
            form,
            text="Register Client",
            bg=self.COLOR_ACENTO,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=10,
            command=self._registrar_cliente,
        ).grid(row=len(campos), column=0, columnspan=2, pady=10)

        list_frame = tk.LabelFrame(
            frame,
            text=" Registered Clients ",
            bg=self.COLOR_PANEL,
            fg=self.COLOR_ACENTO,
            font=("Segoe UI", 10, "bold"),
            bd=2,
        )
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.lista_clientes = tk.Listbox(
            list_frame,
            bg=self.COLOR_ENTRADA,
            fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9),
            relief="flat",
            selectbackground=self.COLOR_ACENTO,
        )
        self.lista_clientes.pack(fill="both", expand=True, padx=8, pady=8)

    def _registrar_cliente(self) -> None:
        try:
            nombre = self._validate_client_name(self.entry_nombre_cli.get())
            documento = self._validate_document(self.entry_doc_cli.get())
            correo = self._validate_email(self.entry_correo_cli.get())
            telefono = self._validate_phone(self.entry_tel_cli.get())

            if self._client_name_exists(nombre):
                raise ErrorValidacion(
                    "full name",
                    f"The client '{nombre}' is already registered."
                )
            if self._client_document_exists(documento):
                raise ErrorValidacion(
                    "ID number",
                    f"The document '{documento}' is already registered."
                )
            if self._client_email_exists(correo):
                raise ErrorValidacion(
                    "email address",
                    f"The email '{correo}' is already registered."
                )

            cliente = Cliente(
                nombre=nombre,
                documento=documento,
                correo=correo,
                telefono=telefono,
            )
            self._clientes.append(cliente)
            self.lista_clientes.insert(
                tk.END,
                f"#{cliente.id}  {cliente.nombre}  |  {cliente.correo}",
            )
            self._limpiar_entradas(
                self.entry_nombre_cli,
                self.entry_doc_cli,
                self.entry_correo_cli,
                self.entry_tel_cli,
            )
            messagebox.showinfo(
                "Client Registered",
                f"Client '{cliente.nombre}' registered successfully.",
            )
            self.logger.info(f"GUI: Client registered -> {cliente.nombre}")
            self._actualizar_combos()

        except ErrorSistema as e:
            messagebox.showerror("Validation Error", str(e))
            self.logger.error(f"GUI: Client registration error -> {e}")

    # Tab 2 - Services

    def _tab_servicios(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb)
        nb.add(frame, text="Services")

        tipo_frame = tk.Frame(frame, bg=self.COLOR_FONDO)
        tipo_frame.pack(fill="x", padx=15, pady=(15, 0))

        tk.Label(
            tipo_frame,
            text="Service type:",
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=(0, 10))

        self.tipo_servicio = tk.StringVar(value="Room")
        for tipo in ("Room", "Equipment", "Consulting"):
            tk.Radiobutton(
                tipo_frame,
                text=tipo,
                variable=self.tipo_servicio,
                value=tipo,
                bg=self.COLOR_FONDO,
                fg=self.COLOR_TEXTO,
                selectcolor=self.COLOR_PANEL,
                activebackground=self.COLOR_FONDO,
                font=("Segoe UI", 9),
                command=self._mostrar_campos_servicio,
            ).pack(side="left", padx=6)

        self.form_serv = tk.LabelFrame(
            frame,
            text=" Service Details ",
            bg=self.COLOR_PANEL,
            fg=self.COLOR_ACENTO,
            font=("Segoe UI", 10, "bold"),
            bd=2,
        )
        self.form_serv.pack(fill="x", padx=15, pady=8)
        self._mostrar_campos_servicio()

        list_frame = tk.LabelFrame(
            frame,
            text=" Created Services ",
            bg=self.COLOR_PANEL,
            fg=self.COLOR_ACENTO,
            font=("Segoe UI", 10, "bold"),
            bd=2,
        )
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.lista_servicios = tk.Listbox(
            list_frame,
            bg=self.COLOR_ENTRADA,
            fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9),
            relief="flat",
            selectbackground=self.COLOR_ACENTO,
        )
        self.lista_servicios.pack(fill="both", expand=True, padx=8, pady=8)

    def _lbl_entry(self, parent, texto, row, attr, width=34) -> tk.Entry:
        tk.Label(
            parent,
            text=texto,
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9),
        ).grid(row=row, column=0, sticky="w", padx=12, pady=5)
        entry = tk.Entry(
            parent,
            width=width,
            bg=self.COLOR_ENTRADA,
            fg=self.COLOR_TEXTO,
            insertbackground=self.COLOR_TEXTO,
            relief="flat",
            font=("Segoe UI", 9),
        )
        entry.grid(row=row, column=1, padx=12, pady=5)
        setattr(self, attr, entry)
        return entry

    def _mostrar_campos_servicio(self) -> None:
        for widget in self.form_serv.winfo_children():
            widget.destroy()

        tipo = self.tipo_servicio.get()
        self._lbl_entry(
            self.form_serv,
            "Service name (unique, min 3):",
            0,
            "sv_nombre",
        )
        self._lbl_entry(
            self.form_serv,
            "Base price per hour (positive number):",
            1,
            "sv_precio",
        )

        if tipo == "Room":
            self._lbl_entry(
                self.form_serv,
                "Maximum capacity (positive integer):",
                2,
                "sv_cap",
            )
            tk.Label(
                self.form_serv,
                text="Has projector?",
                bg=self.COLOR_PANEL,
                fg=self.COLOR_TEXTO,
                font=("Segoe UI", 9),
            ).grid(row=3, column=0, sticky="w", padx=12, pady=5)
            self.sv_proyector = tk.BooleanVar()
            tk.Checkbutton(
                self.form_serv,
                variable=self.sv_proyector,
                bg=self.COLOR_PANEL,
                activebackground=self.COLOR_PANEL,
            ).grid(row=3, column=1, sticky="w", padx=12)

        elif tipo == "Equipment":
            self._lbl_entry(
                self.form_serv,
                "Equipment type (letters and spaces, min 3):",
                2,
                "sv_tipo_eq",
            )
            self._lbl_entry(
                self.form_serv,
                "Available units (integer, 0 or more):",
                3,
                "sv_unidades",
            )

        elif tipo == "Consulting":
            self._lbl_entry(
                self.form_serv,
                "Specialization area (letters and spaces, min 3):",
                2,
                "sv_area",
            )
            tk.Label(
                self.form_serv,
                text="Advisor level:",
                bg=self.COLOR_PANEL,
                fg=self.COLOR_TEXTO,
                font=("Segoe UI", 9),
            ).grid(row=3, column=0, sticky="w", padx=12, pady=5)
            self.sv_nivel = ttk.Combobox(
                self.form_serv,
                values=["junior", "senior", "expert"],
                state="readonly",
                width=15,
                font=("Segoe UI", 9),
            )
            self.sv_nivel.set("junior")
            self.sv_nivel.grid(row=3, column=1, sticky="w", padx=12)
            self._lbl_entry(
                self.form_serv,
                "Minimum duration (1-150, e.g. 4.15):",
                4,
                "sv_dur_min",
            )

        tk.Button(
            self.form_serv,
            text="Create Service",
            bg=self.COLOR_ACENTO,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=10,
            command=self._crear_servicio,
        ).grid(row=10, column=0, columnspan=2, pady=10)

    def _crear_servicio(self) -> None:
        try:
            tipo = self.tipo_servicio.get()
            nombre = self._validate_service_name(self.sv_nombre.get())
            precio = self._validate_positive_decimal(self.sv_precio.get(), "base price per hour")

            if self._service_name_exists(nombre):
                raise ErrorValidacion(
                    "service name",
                    f"The service '{nombre}' is already created."
                )

            if tipo == "Room":
                capacidad = self._validate_positive_integer(
                    self.sv_cap.get(),
                    "maximum capacity",
                    minimum=1,
                )
                servicio = ReservaSala(
                    nombre=nombre,
                    precio_base=precio,
                    capacidad_maxima=capacidad,
                    tiene_proyector=self.sv_proyector.get(),
                )
            elif tipo == "Equipment":
                tipo_equipo = self._validate_simple_text(
                    self.sv_tipo_eq.get(),
                    "equipment type",
                    min_len=3,
                )
                unidades = self._validate_integer(
                    self.sv_unidades.get(),
                    "available units",
                    minimum=0,
                )
                servicio = AlquilerEquipos(
                    nombre=nombre,
                    precio_base=precio,
                    tipo_equipo=tipo_equipo,
                    unidades_disponibles=unidades,
                )
            else:
                area = self._validate_simple_text(
                    self.sv_area.get(),
                    "specialization area",
                    min_len=3,
                )
                nivel = self.sv_nivel.get()
                nivel_backend = "experto" if nivel == "expert" else nivel
                duracion_minima = self._validate_hour_value(
                    self.sv_dur_min.get(),
                    "minimum duration",
                )
                servicio = AsesoriaEspecializada(
                    nombre=nombre,
                    precio_base=precio,
                    area_especializacion=area,
                    nivel=nivel_backend,
                    duracion_minima=duracion_minima,
                )

            self._servicios.append(servicio)
            self.lista_servicios.insert(
                tk.END,
                f"#{servicio.id}  [{tipo}]  {nombre}  |  ${precio:,.0f}/h",
            )
            self._limpiar_servicios_form(tipo)
            messagebox.showinfo(
                "Service Created",
                f"Service '{nombre}' created successfully.",
            )
            self.logger.info(f"GUI: Service created -> {nombre}")
            self._actualizar_combos()

        except ErrorSistema as e:
            messagebox.showerror("Validation Error", str(e))
            self.logger.error(f"GUI: Service creation error -> {e}")
        except ValueError as e:
            messagebox.showerror(
                "Format Error",
                f"Please verify that numeric fields contain valid numbers.\n{e}",
            )

    # Tab 3 - Reservations

    def _tab_reservas(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb)
        nb.add(frame, text="Reservations")

        form = tk.LabelFrame(
            frame,
            text=" New Reservation ",
            bg=self.COLOR_PANEL,
            fg=self.COLOR_ACENTO,
            font=("Segoe UI", 10, "bold"),
            bd=2,
        )
        form.pack(fill="x", padx=15, pady=15)

        tk.Label(
            form,
            text="Client:",
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9),
        ).grid(row=0, column=0, sticky="w", padx=12, pady=6)
        self.combo_cliente = ttk.Combobox(
            form,
            state="readonly",
            width=35,
            font=("Segoe UI", 9),
        )
        self.combo_cliente.grid(row=0, column=1, padx=12, pady=6)

        tk.Label(
            form,
            text="Service:",
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9),
        ).grid(row=1, column=0, sticky="w", padx=12, pady=6)
        self.combo_servicio = ttk.Combobox(
            form,
            state="readonly",
            width=35,
            font=("Segoe UI", 9),
        )
        self.combo_servicio.grid(row=1, column=1, padx=12, pady=6)

        tk.Label(
            form,
            text="Duration in hours (1-150, e.g. 4.15):",
            bg=self.COLOR_PANEL,
            fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9),
        ).grid(row=2, column=0, sticky="w", padx=12, pady=6)
        self.entry_duracion = tk.Entry(
            form,
            width=15,
            bg=self.COLOR_ENTRADA,
            fg=self.COLOR_TEXTO,
            insertbackground=self.COLOR_TEXTO,
            relief="flat",
            font=("Segoe UI", 9),
        )
        self.entry_duracion.grid(row=2, column=1, sticky="w", padx=12)

        btn_frame = tk.Frame(form, bg=self.COLOR_PANEL)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        for text, cmd, color in [
            ("Create Reservation", self._crear_reserva, self.COLOR_ACENTO),
            ("Confirm", self._confirmar_reserva, "#16a34a"),
            ("Process", self._procesar_reserva, "#0284c7"),
            ("Cancel", self._cancelar_reserva, "#dc2626"),
        ]:
            tk.Button(
                btn_frame,
                text=text,
                bg=color,
                fg="white",
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=4,
                command=cmd,
            ).pack(side="left", padx=5)

        list_frame = tk.LabelFrame(
            frame,
            text=" System Reservations ",
            bg=self.COLOR_PANEL,
            fg=self.COLOR_ACENTO,
            font=("Segoe UI", 10, "bold"),
            bd=2,
        )
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.lista_reservas = tk.Listbox(
            list_frame,
            bg=self.COLOR_ENTRADA,
            fg=self.COLOR_TEXTO,
            font=("Segoe UI", 9),
            relief="flat",
            selectbackground=self.COLOR_ACENTO,
        )
        self.lista_reservas.pack(fill="both", expand=True, padx=8, pady=8)

    def _crear_reserva(self) -> None:
        try:
            idx_cli = self.combo_cliente.current()
            idx_srv = self.combo_servicio.current()
            if idx_cli < 0 or idx_srv < 0:
                messagebox.showwarning(
                    "Missing Data",
                    "Please select a client and a service.",
                )
                return

            duracion = self._validate_hour_value(
                self.entry_duracion.get(),
                "duration in hours",
            )
            cliente = self._clientes[idx_cli]
            servicio = self._servicios[idx_srv]

            reserva = Reserva(
                cliente=cliente,
                servicio=servicio,
                duracion=duracion,
            )
            self._reservas.append(reserva)
            self._actualizar_lista_reservas()
            messagebox.showinfo("Reservation Created", f"{reserva}")
            self.logger.info(f"GUI: Reservation created -> {reserva}")

        except ErrorSistema as e:
            messagebox.showerror("Validation Error", str(e))
            self.logger.error(f"GUI: Reservation creation error -> {e}")
        except ValueError:
            messagebox.showerror(
                "Format Error",
                "Duration must be a numeric value.",
            )

    def _reserva_seleccionada(self):
        sel = self.lista_reservas.curselection()
        if not sel:
            messagebox.showwarning(
                "No Selection",
                "Please select a reservation.",
            )
            return None
        return self._reservas[sel[0]]

    def _confirmar_reserva(self) -> None:
        reserva = self._reserva_seleccionada()
        if not reserva:
            return
        try:
            msg = reserva.confirmar()
            self._actualizar_lista_reservas()
            messagebox.showinfo("Confirmed", msg)
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e))
            self.logger.error(f"GUI: Reservation confirmation error -> {e}")

    def _procesar_reserva(self) -> None:
        reserva = self._reserva_seleccionada()
        if not reserva:
            return
        try:
            msg = reserva.procesar()
            self._actualizar_lista_reservas()
            messagebox.showinfo("Processed", msg)
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e))
            self.logger.error(f"GUI: Reservation processing error -> {e}")

    def _cancelar_reserva(self) -> None:
        reserva = self._reserva_seleccionada()
        if not reserva:
            return
        try:
            msg = reserva.cancelar("Cancelled from the interface")
            self._actualizar_lista_reservas()
            messagebox.showinfo("Cancelled", msg)
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e))
            self.logger.error(f"GUI: Reservation cancellation error -> {e}")

    def _actualizar_lista_reservas(self) -> None:
        self.lista_reservas.delete(0, tk.END)
        for reserva in self._reservas:
            self.lista_reservas.insert(tk.END, str(reserva))

    # Tab 4 - Logs

    def _tab_logs(self, nb: ttk.Notebook) -> None:
        frame = ttk.Frame(nb)
        nb.add(frame, text="Logs")

        tk.Label(
            frame,
            text="Contents of logs/sistema.log",
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO,
            font=("Segoe UI", 10, "bold"),
        ).pack(pady=(12, 4))

        self.area_logs = scrolledtext.ScrolledText(
            frame,
            bg=self.COLOR_ENTRADA,
            fg="#86efac",
            font=("Consolas", 9),
            relief="flat",
            state="disabled",
        )
        self.area_logs.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        tk.Button(
            frame,
            text="Refresh Logs",
            bg=self.COLOR_ACENTO,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=10,
            command=self._cargar_logs,
        ).pack(pady=(0, 10))

        self._cargar_logs()

    def _cargar_logs(self) -> None:
        try:
            with open("logs/sistema.log", "r", encoding="utf-8") as file:
                contenido = file.read()
            self.area_logs.configure(state="normal")
            self.area_logs.delete("1.0", tk.END)
            self.area_logs.insert(tk.END, contenido)
            self.area_logs.configure(state="disabled")
            self.area_logs.see(tk.END)
        except FileNotFoundError:
            self.area_logs.configure(state="normal")
            self.area_logs.delete("1.0", tk.END)
            self.area_logs.insert(
                tk.END,
                "No log file has been generated yet.\n",
            )
            self.area_logs.configure(state="disabled")

    # Utilities

    def _validate_required_text(
        self,
        value: str,
        field_label: str,
        min_len: int,
        max_len: int | None = None,
    ) -> str:
        if value is None:
            raise ErrorValidacion(field_label, "this field is required")
        cleaned = " ".join(str(value).split()).strip()
        if cleaned == "":
            raise ErrorValidacion(field_label, "this field cannot be empty or only spaces")
        if len(cleaned) < min_len:
            raise ErrorValidacion(
                field_label,
                f"must have at least {min_len} characters",
            )
        if max_len is not None and len(cleaned) > max_len:
            raise ErrorValidacion(
                field_label,
                f"must have at most {max_len} characters",
            )
        return cleaned

    def _validate_client_name(self, value: str) -> str:
        cleaned = self._validate_required_text(value, "full name", 3, 100)
        if not self.NAME_PATTERN.fullmatch(cleaned):
            raise ErrorValidacion(
                "full name",
                "use letters, accents, ñ and spaces only",
            )
        return cleaned

    def _validate_service_name(self, value: str) -> str:
        cleaned = self._validate_required_text(value, "service name", 3, 100)
        if not self.SIMPLE_TEXT_PATTERN.fullmatch(cleaned):
            raise ErrorValidacion(
                "service name",
                "use letters, numbers, spaces and hyphens only",
            )
        return cleaned

    def _validate_simple_text(self, value: str, field_label: str, min_len: int = 3) -> str:
        cleaned = self._validate_required_text(value, field_label, min_len, 100)
        if not self.SIMPLE_TEXT_PATTERN.fullmatch(cleaned):
            raise ErrorValidacion(
                field_label,
                "use only letters, numbers, spaces and hyphens",
            )
        return cleaned

    def _validate_document(self, value: str) -> str:
        cleaned = self._validate_required_text(value, "ID number", 6, 15)
        if not cleaned.isdigit():
            raise ErrorValidacion(
                "ID number",
                "use digits only, between 6 and 15 characters",
            )
        return cleaned

    def _validate_email(self, value: str) -> str:
        cleaned = self._validate_required_text(value, "email address", 6, 254).lower()
        if not self.EMAIL_PATTERN.fullmatch(cleaned):
            raise ErrorValidacion(
                "email address",
                "format example: correo@gmail.com",
            )
        return cleaned

    def _validate_phone(self, value: str) -> str:
        cleaned = self._validate_required_text(value, "phone number", 10, 15)
        if not cleaned.isdigit():
            raise ErrorValidacion(
                "phone number",
                "use digits only, minimum 10 characters",
            )
        if not self.PHONE_PATTERN.fullmatch(cleaned):
            raise ErrorValidacion(
                "phone number",
                "avoid repeated impossible values like 0000000000 or 1111111111",
            )
        return cleaned

    def _validate_positive_decimal(self, value: str, field_label: str) -> float:
        cleaned = self._validate_required_text(value, field_label, 1, 20)
        if not self.DECIMAL_PATTERN.fullmatch(cleaned):
            raise ErrorValidacion(
                field_label,
                "use a positive numeric value only",
            )
        result = float(cleaned)
        if result <= 0:
            raise ErrorValidacion(field_label, "must be greater than 0")
        return result

    def _validate_integer(self, value: str, field_label: str, minimum: int = 0) -> int:
        cleaned = self._validate_required_text(value, field_label, 1, 20)
        if not self.INTEGER_PATTERN.fullmatch(cleaned):
            raise ErrorValidacion(
                field_label,
                "use digits only",
            )
        result = int(cleaned)
        if result < minimum:
            raise ErrorValidacion(
                field_label,
                f"must be greater than or equal to {minimum}",
            )
        return result

    def _validate_positive_integer(self, value: str, field_label: str, minimum: int = 1) -> int:
        return self._validate_integer(value, field_label, minimum=minimum)

    def _validate_hour_value(self, value: str, field_label: str) -> float:
        cleaned = self._validate_required_text(value, field_label, 1, 20)
        if not self.DECIMAL_PATTERN.fullmatch(cleaned):
            raise ErrorValidacion(
                field_label,
                "use a numeric value with dot as decimal separator (for example 4.15)",
            )
        result = float(cleaned)
        if not (1 <= result <= 150):
            raise ErrorValidacion(
                field_label,
                "must be between 1 and 150",
            )
        return result

    def _client_name_exists(self, name: str) -> bool:
        target = self._normalize_key(name)
        return any(self._normalize_key(cliente.nombre) == target for cliente in self._clientes)

    def _client_document_exists(self, document: str) -> bool:
        target = document.strip()
        return any(cliente.documento.strip() == target for cliente in self._clientes)

    def _client_email_exists(self, email: str) -> bool:
        target = email.strip().lower()
        return any(cliente.correo.strip().lower() == target for cliente in self._clientes)

    def _service_name_exists(self, name: str) -> bool:
        target = self._normalize_key(name)
        return any(self._normalize_key(servicio.nombre) == target for servicio in self._servicios)

    @staticmethod
    def _normalize_key(value: str) -> str:
        return " ".join(str(value).split()).casefold().strip()

    def _actualizar_combos(self) -> None:
        self.combo_cliente["values"] = [f"#{cliente.id} {cliente.nombre}" for cliente in self._clientes]
        self.combo_servicio["values"] = [f"#{servicio.id} {servicio.nombre}" for servicio in self._servicios]

    def _limpiar_servicios_form(self, tipo: str) -> None:
        if hasattr(self, "sv_nombre"):
            self.sv_nombre.delete(0, tk.END)
        if hasattr(self, "sv_precio"):
            self.sv_precio.delete(0, tk.END)
        if tipo == "Room" and hasattr(self, "sv_cap"):
            self.sv_cap.delete(0, tk.END)
            if hasattr(self, "sv_proyector"):
                self.sv_proyector.set(False)
        elif tipo == "Equipment":
            if hasattr(self, "sv_tipo_eq"):
                self.sv_tipo_eq.delete(0, tk.END)
            if hasattr(self, "sv_unidades"):
                self.sv_unidades.delete(0, tk.END)
        elif tipo == "Consulting":
            if hasattr(self, "sv_area"):
                self.sv_area.delete(0, tk.END)
            if hasattr(self, "sv_dur_min"):
                self.sv_dur_min.delete(0, tk.END)
            if hasattr(self, "sv_nivel"):
                self.sv_nivel.set("junior")

    @staticmethod
    def _limpiar_entradas(*entradas) -> None:
        for entrada in entradas:
            entrada.delete(0, tk.END)