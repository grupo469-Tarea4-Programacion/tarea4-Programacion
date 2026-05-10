"""
Graphical User Interface module using Tkinter.
Author: Integrante Nasly Isabella Velez Muñoz - Integrator
Description: Graphical interface connecting all features of the
             Software FJ system: clients, services, and reservations.
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
from excepciones.excepciones import ErrorSistema


class InterfazSoftwareFJ(tk.Tk):
    """
    Main application window for Software FJ.
    Tabs: Clients, Services, Reservations, System Logs.
    """

    C_BG      = "#1e1e2e"
    C_PANEL   = "#2a2a3e"
    C_ACCENT  = "#7c3aed"
    C_TEXT    = "#e2e8f0"
    C_INPUT   = "#3b3b52"
    C_HINT    = "#94a3b8"
    C_BORDER  = "#4c4c6e"
    C_SUCCESS = "#22c55e"
    C_WARN    = "#f59e0b"
    C_ERROR   = "#ef4444"

    def __init__(self):
        super().__init__()
        self._logger = Logger()
        self._clients: list = []
        self._services: list = []
        self._reservations: list = []
        self._setup_window()
        self._build_ui()

    # Window setup

    def _setup_window(self) -> None:
        self.title("Software FJ  -  Integrated Management System")
        self.geometry("1000x700")
        self.minsize(860, 600)
        self.configure(bg=self.C_BG)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "TNotebook",
            background=self.C_BG,
            borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            background=self.C_PANEL,
            foreground=self.C_TEXT,
            padding=[20, 9],
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.C_ACCENT)],
            foreground=[("selected", "white")]
        )
        style.configure("TFrame", background=self.C_BG)
        style.configure(
            "TCombobox",
            fieldbackground=self.C_INPUT,
            background=self.C_INPUT,
            foreground=self.C_TEXT,
            selectbackground=self.C_ACCENT
        )

    # Main UI 

    def _build_ui(self) -> None:
        # Header bar
        header = tk.Frame(self, bg=self.C_ACCENT, height=58)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text="SOFTWARE FJ  |  Integrated Client, Service and Reservation Management",
            font=("Segoe UI", 13, "bold"),
            bg=self.C_ACCENT,
            fg="white"
        ).pack(expand=True)

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self._tab_clients(nb)
        self._tab_services(nb)
        self._tab_reservations(nb)
        self._tab_logs(nb)

        # Status bar
        self._status_var = tk.StringVar(value="System ready.")
        bar = tk.Frame(self, bg=self.C_PANEL, height=26)
        bar.pack(fill="x", side="bottom")
        tk.Label(
            bar,
            textvariable=self._status_var,
            bg=self.C_PANEL,
            fg=self.C_HINT,
            font=("Segoe UI", 8),
            anchor="w",
            padx=12
        ).pack(fill="x", pady=4)

    def _status(self, msg: str) -> None:
        self._status_var.set(msg)

    # Reusable widget builders 

    def _field(
        self,
        parent,
        label: str,
        attr: str,
        hint: str,
        row: int,
        width: int = 34
    ) -> tk.Entry:
        """
        Builds a label + entry + hint block using grid layout.
        Each field occupies 3 grid rows: label, entry, hint.
        """
        r = row * 3
        tk.Label(
            parent,
            text=label,
            bg=self.C_PANEL,
            fg=self.C_TEXT,
            font=("Segoe UI", 9, "bold"),
            anchor="w"
        ).grid(row=r, column=0, sticky="w", padx=14, pady=(10, 0))

        entry = tk.Entry(
            parent,
            width=width,
            bg=self.C_INPUT,
            fg=self.C_TEXT,
            insertbackground=self.C_TEXT,
            relief="flat",
            font=("Segoe UI", 9),
            highlightthickness=1,
            highlightbackground=self.C_BORDER,
            highlightcolor=self.C_ACCENT
        )
        entry.grid(row=r + 1, column=0, sticky="w", padx=14, pady=2)
        setattr(self, attr, entry)

        tk.Label(
            parent,
            text=hint,
            bg=self.C_PANEL,
            fg=self.C_HINT,
            font=("Segoe UI", 7, "italic"),
            anchor="w"
        ).grid(row=r + 2, column=0, sticky="w", padx=16)

        return entry

    def _btn(
        self, parent, text: str, cmd, color: str = None, width: int = 18
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            bg=color or self.C_ACCENT,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=5,
            width=width,
            command=cmd
        )

    def _section(self, parent, title: str, side="left", fill="y", expand=False):
        frame = tk.LabelFrame(
            parent,
            text=f"  {title}  ",
            bg=self.C_PANEL,
            fg=self.C_ACCENT,
            font=("Segoe UI", 10, "bold"),
            bd=2,
            relief="groove"
        )
        frame.pack(side=side, fill=fill, expand=expand, padx=6, pady=6)
        return frame

    @staticmethod
    def _clear(*entries) -> None:
        for e in entries:
            if isinstance(e, tk.Entry):
                e.delete(0, tk.END)

    def _update_combos(self) -> None:
        self._combo_client["values"] = [
            f"#{c.id}  {c.nombre}" for c in self._clients
        ]
        self._combo_service["values"] = [
            f"#{s.id}  {s.nombre}" for s in self._services
        ]

    # Duplicate helpers 

    def _name_taken(self, name: str) -> bool:
        return any(
            c.nombre.strip().lower() == name.strip().lower()
            for c in self._clients
        )

    def _doc_taken(self, doc: str) -> bool:
        return any(c.documento == doc.strip() for c in self._clients)

    def _email_taken(self, email: str) -> bool:
        return any(
            c.correo.strip().lower() == email.strip().lower()
            for c in self._clients
        )

    def _service_name_taken(self, name: str) -> bool:
        return any(
            s.nombre.strip().lower() == name.strip().lower()
            for s in self._services
        )

    # GUI-level validators 

    @staticmethod
    def _gui_validate_duration(raw: str) -> float:
        """Duration must be a number between 1 and 150."""
        try:
            val = float(raw)
        except ValueError:
            raise ValueError(
                "Duration must be a number.\n"
                "Examples: 1  /  2.5  /  10"
            )
        if val < 1 or val > 150:
            raise ValueError(
                f"Duration must be between 1 and 150 hours.\n"
                f"Value entered: {raw}"
            )
        return val

    @staticmethod
    def _gui_validate_price(raw: str) -> float:
        """Price must be a positive number."""
        try:
            val = float(raw)
        except ValueError:
            raise ValueError(
                "Base price must be a number.\n"
                "Example: 80000"
            )
        if val <= 0:
            raise ValueError(
                "Base price must be greater than zero.\n"
                f"Value entered: {raw}"
            )
        return val

    @staticmethod
    def _gui_validate_positive_int(raw: str, field: str) -> int:
        """Field must be a positive whole number."""
        try:
            val = int(raw)
        except ValueError:
            raise ValueError(
                f"{field} must be a whole number with no decimals.\n"
                f"Example: 5"
            )
        if val <= 0:
            raise ValueError(
                f"{field} must be greater than zero.\n"
                f"Value entered: {raw}"
            )
        return val

    @staticmethod
    def _is_impossible_phone(digits: str) -> bool:
        """Returns True if all digits are the same, e.g. 0000000000."""
        return len(set(digits)) == 1 if digits else False

    #  TAB 1 — CLIENTS

    def _tab_clients(self, nb: ttk.Notebook) -> None:
        outer = ttk.Frame(nb)
        nb.add(outer, text="Clients")

        wrapper = tk.Frame(outer, bg=self.C_BG)
        wrapper.pack(fill="both", expand=True, padx=6, pady=6)

        # Left — registration form
        left_wrap = tk.Frame(wrapper, bg=self.C_BG)
        left_wrap.pack(side="left", fill="y")

        form = self._section(left_wrap, "Register New Client", side="top", fill="x")

        self._field(
            form, "Full Name", "_cli_name",
            hint="Letters, accents and spaces only. Min 3 characters.",
            row=0
        )
        self._field(
            form, "ID Document (cedula)", "_cli_doc",
            hint="Positive numbers only. Min 6, max 15 digits.",
            row=1
        )
        self._field(
            form, "Email Address", "_cli_email",
            hint="Format: name@domain.com",
            row=2
        )
        self._field(
            form, "Phone Number", "_cli_phone",
            hint="Numbers only, minimum 10 digits. Example: 3101234567",
            row=3
        )

        self._btn(
            form, "Register Client", self._register_client
        ).grid(row=13, column=0, padx=14, pady=14, sticky="w")

        # Right — client list
        right_wrap = tk.Frame(wrapper, bg=self.C_BG)
        right_wrap.pack(side="right", fill="both", expand=True)

        list_frame = self._section(
            right_wrap, "Registered Clients",
            side="top", fill="both", expand=True
        )

        self._clients_box = tk.Listbox(
            list_frame,
            bg=self.C_INPUT,
            fg=self.C_TEXT,
            font=("Consolas", 9),
            relief="flat",
            selectbackground=self.C_ACCENT,
            activestyle="none"
        )
        self._clients_box.pack(fill="both", expand=True, padx=8, pady=8)

        self._clients_count = tk.StringVar(value="Total: 0 clients")
        tk.Label(
            right_wrap,
            textvariable=self._clients_count,
            bg=self.C_BG,
            fg=self.C_HINT,
            font=("Segoe UI", 8)
        ).pack(anchor="e", padx=8)

    def _register_client(self) -> None:
        name  = self._cli_name.get().strip()
        doc   = self._cli_doc.get().strip()
        email = self._cli_email.get().strip()
        phone = self._cli_phone.get().strip()

        # Duplicate checks before creating object
        if self._name_taken(name):
            messagebox.showwarning(
                "Duplicate Name",
                f"A client named '{name}' already exists.\n"
                "Please verify the information."
            )
            return

        if self._doc_taken(doc):
            messagebox.showwarning(
                "Duplicate Document",
                f"Document '{doc}' is already registered."
            )
            return

        if self._email_taken(email):
            messagebox.showwarning(
                "Duplicate Email",
                f"Email '{email}' is already linked to another client."
            )
            return

        # Impossible phone check at GUI level
        digits = phone.lstrip("+").replace("-", "").replace(" ", "")
        if digits.isdigit() and digits and self._is_impossible_phone(digits):
            messagebox.showerror(
                "Invalid Phone Number",
                f"'{phone}' is not a valid phone number.\n"
                "All digits cannot be identical (e.g. 0000000000 or 1111111111)."
            )
            return

        try:
            client = Cliente(
                nombre=name,
                documento=doc,
                correo=email,
                telefono=phone
            )
            self._clients.append(client)
            self._clients_box.insert(
                tk.END,
                f"  #{client.id:<4}  {client.nombre:<26}  {client.correo}"
            )
            self._clients_count.set(f"Total: {len(self._clients)} client(s)")
            self._clear(
                self._cli_name, self._cli_doc,
                self._cli_email, self._cli_phone
            )
            self._update_combos()
            self._status(f"Client '{client.nombre}' registered successfully.")
            self._logger.info(f"GUI: Client registered -> {client.nombre}")
            messagebox.showinfo(
                "Client Registered",
                f"Client '{client.nombre}' was registered successfully."
            )

        except ErrorSistema as e:
            messagebox.showerror("Validation Error", str(e))
            self._logger.error(f"GUI: Error registering client -> {e}")
            self._status(f"Error: {e}")

    #  TAB 2 — SERVICES

    def _tab_services(self, nb: ttk.Notebook) -> None:
        outer = ttk.Frame(nb)
        nb.add(outer, text="Services")

        wrapper = tk.Frame(outer, bg=self.C_BG)
        wrapper.pack(fill="both", expand=True, padx=6, pady=6)

        left_wrap = tk.Frame(wrapper, bg=self.C_BG)
        left_wrap.pack(side="left", fill="y")

        # Service type selector
        type_frame = self._section(
            left_wrap, "Service Type", side="top", fill="x"
        )
        self._svc_type = tk.StringVar(value="Room")
        for label, val in [
            ("Room Reservation", "Room"),
            ("Equipment Rental", "Equipment"),
            ("Specialized Advisory", "Advisory"),
        ]:
            tk.Radiobutton(
                type_frame,
                text=label,
                variable=self._svc_type,
                value=val,
                bg=self.C_PANEL,
                fg=self.C_TEXT,
                selectcolor=self.C_INPUT,
                activebackground=self.C_PANEL,
                activeforeground=self.C_TEXT,
                font=("Segoe UI", 9),
                command=self._rebuild_service_form
            ).pack(anchor="w", padx=14, pady=4)

        # Dynamic form placeholder
        self._svc_form_frame = self._section(
            left_wrap, "Service Details", side="top", fill="x"
        )
        self._rebuild_service_form()

        # Right — service list
        right_wrap = tk.Frame(wrapper, bg=self.C_BG)
        right_wrap.pack(side="right", fill="both", expand=True)

        list_frame = self._section(
            right_wrap, "Created Services",
            side="top", fill="both", expand=True
        )
        self._services_box = tk.Listbox(
            list_frame,
            bg=self.C_INPUT,
            fg=self.C_TEXT,
            font=("Consolas", 9),
            relief="flat",
            selectbackground=self.C_ACCENT,
            activestyle="none"
        )
        self._services_box.pack(fill="both", expand=True, padx=8, pady=8)

        self._services_count = tk.StringVar(value="Total: 0 services")
        tk.Label(
            right_wrap,
            textvariable=self._services_count,
            bg=self.C_BG,
            fg=self.C_HINT,
            font=("Segoe UI", 8)
        ).pack(anchor="e", padx=8)

    def _svc_field(
        self, label: str, attr: str, hint: str, row: int
    ) -> tk.Entry:
        """Builds a labeled field inside the dynamic service form."""
        return self._field(
            self._svc_form_frame, label, attr, hint, row, width=30
        )

    def _rebuild_service_form(self) -> None:
        for w in self._svc_form_frame.winfo_children():
            w.destroy()

        stype = self._svc_type.get()

        self._svc_field(
            "Service Name", "_sv_name",
            hint="Unique name, no special symbols.",
            row=0
        )
        self._svc_field(
            "Base Price per Hour ($)", "_sv_price",
            hint="Positive number only. Example: 80000",
            row=1
        )

        if stype == "Room":
            self._svc_field(
                "Max Capacity (people)", "_sv_cap",
                hint="Positive whole number. Example: 10",
                row=2
            )
            tk.Label(
                self._svc_form_frame,
                text="Includes Projector?",
                bg=self.C_PANEL, fg=self.C_TEXT,
                font=("Segoe UI", 9, "bold")
            ).grid(row=9, column=0, sticky="w", padx=14, pady=(10, 0))
            self._sv_projector = tk.BooleanVar()
            tk.Checkbutton(
                self._svc_form_frame,
                variable=self._sv_projector,
                text="Yes",
                bg=self.C_PANEL, fg=self.C_TEXT,
                selectcolor=self.C_INPUT,
                activebackground=self.C_PANEL,
                activeforeground=self.C_TEXT,
                font=("Segoe UI", 9)
            ).grid(row=10, column=0, sticky="w", padx=14, pady=2)

        elif stype == "Equipment":
            self._svc_field(
                "Equipment Type", "_sv_eq_type",
                hint="Description of the equipment. Example: Dell Laptop",
                row=2
            )
            self._svc_field(
                "Available Units", "_sv_units",
                hint="Positive whole number. Example: 5",
                row=3
            )

        elif stype == "Advisory":
            self._svc_field(
                "Area of Expertise", "_sv_area",
                hint="Example: Cybersecurity, Networks, Data Science",
                row=2
            )
            tk.Label(
                self._svc_form_frame,
                text="Advisor Level",
                bg=self.C_PANEL, fg=self.C_TEXT,
                font=("Segoe UI", 9, "bold")
            ).grid(row=9, column=0, sticky="w", padx=14, pady=(10, 0))
            self._sv_level = ttk.Combobox(
                self._svc_form_frame,
                values=["Junior", "Senior", "Expert"],
                state="readonly",
                width=20,
                font=("Segoe UI", 9)
            )
            self._sv_level.set("Junior")
            self._sv_level.grid(row=10, column=0, sticky="w", padx=14, pady=2)
            self._svc_field(
                "Minimum Duration (hours)", "_sv_min_dur",
                hint="Numbers only, range 1-150. Example: 2 or 2.5",
                row=4
            )

        self._btn(
            self._svc_form_frame, "Create Service", self._create_service
        ).grid(row=30, column=0, padx=14, pady=14, sticky="w")

    def _create_service(self) -> None:
        stype = self._svc_type.get()
        name  = self._sv_name.get().strip()

        if not name:
            messagebox.showerror(
                "Missing Data",
                "Service name cannot be empty."
            )
            return

        if self._service_name_taken(name):
            messagebox.showwarning(
                "Duplicate Service",
                f"A service named '{name}' already exists.\n"
                "Please choose a different name."
            )
            return

        try:
            price = self._gui_validate_price(self._sv_price.get())

            if stype == "Room":
                capacity = self._gui_validate_positive_int(
                    self._sv_cap.get(), "Max Capacity"
                )
                service = ReservaSala(
                    nombre=name,
                    precio_base=price,
                    capacidad_maxima=capacity,
                    tiene_proyector=self._sv_projector.get()
                )

            elif stype == "Equipment":
                units = self._gui_validate_positive_int(
                    self._sv_units.get(), "Available Units"
                )
                service = AlquilerEquipos(
                    nombre=name,
                    precio_base=price,
                    tipo_equipo=self._sv_eq_type.get().strip(),
                    unidades_disponibles=units
                )

            else:
                level_map = {
                    "Junior": "junior",
                    "Senior": "senior",
                    "Expert": "experto"
                }
                nivel = level_map.get(self._sv_level.get(), "junior")
                min_dur = self._gui_validate_duration(self._sv_min_dur.get())
                service = AsesoriaEspecializada(
                    nombre=name,
                    precio_base=price,
                    area_especializacion=self._sv_area.get().strip(),
                    nivel=nivel,
                    duracion_minima=min_dur
                )

            self._services.append(service)
            self._services_box.insert(
                tk.END,
                f"  #{service.id:<4}  [{stype:<9}]  {name:<22}  ${price:,.0f}/h"
            )
            self._services_count.set(f"Total: {len(self._services)} service(s)")
            self._update_combos()
            self._status(f"Service '{name}' created successfully.")
            self._logger.info(f"GUI: Service created -> {name}")
            messagebox.showinfo(
                "Service Created",
                f"Service '{name}' was created successfully."
            )

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            self._logger.error(f"GUI: Input error creating service -> {e}")
            self._status(f"Input error: {e}")
        except ErrorSistema as e:
            messagebox.showerror("Service Error", str(e))
            self._logger.error(f"GUI: Error creating service -> {e}")
            self._status(f"Error: {e}")

    #  TAB 3 — RESERVATIONS

    def _tab_reservations(self, nb: ttk.Notebook) -> None:
        outer = ttk.Frame(nb)
        nb.add(outer, text="Reservations")

        wrapper = tk.Frame(outer, bg=self.C_BG)
        wrapper.pack(fill="both", expand=True, padx=6, pady=6)

        left_wrap = tk.Frame(wrapper, bg=self.C_BG)
        left_wrap.pack(side="left", fill="y")

        form = self._section(left_wrap, "New Reservation", side="top", fill="x")

        # Client combo
        tk.Label(
            form, text="Client",
            bg=self.C_PANEL, fg=self.C_TEXT,
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 0))
        self._combo_client = ttk.Combobox(
            form, state="readonly", width=34, font=("Segoe UI", 9)
        )
        self._combo_client.grid(row=1, column=0, sticky="w", padx=14, pady=2)
        tk.Label(
            form, text="Select a registered client from the list.",
            bg=self.C_PANEL, fg=self.C_HINT,
            font=("Segoe UI", 7, "italic"), anchor="w"
        ).grid(row=2, column=0, sticky="w", padx=16)

        # Service combo
        tk.Label(
            form, text="Service",
            bg=self.C_PANEL, fg=self.C_TEXT,
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).grid(row=3, column=0, sticky="w", padx=14, pady=(10, 0))
        self._combo_service = ttk.Combobox(
            form, state="readonly", width=34, font=("Segoe UI", 9)
        )
        self._combo_service.grid(row=4, column=0, sticky="w", padx=14, pady=2)
        tk.Label(
            form, text="Select an available service from the list.",
            bg=self.C_PANEL, fg=self.C_HINT,
            font=("Segoe UI", 7, "italic"), anchor="w"
        ).grid(row=5, column=0, sticky="w", padx=16)

        # Duration
        tk.Label(
            form, text="Duration (hours)",
            bg=self.C_PANEL, fg=self.C_TEXT,
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).grid(row=6, column=0, sticky="w", padx=14, pady=(10, 0))
        self._entry_duration = tk.Entry(
            form, width=22,
            bg=self.C_INPUT, fg=self.C_TEXT,
            insertbackground=self.C_TEXT,
            relief="flat", font=("Segoe UI", 9),
            highlightthickness=1,
            highlightbackground=self.C_BORDER,
            highlightcolor=self.C_ACCENT
        )
        self._entry_duration.grid(row=7, column=0, sticky="w", padx=14, pady=2)
        tk.Label(
            form,
            text="Numbers only, range 1-150. Format: 4 or 4.5",
            bg=self.C_PANEL, fg=self.C_HINT,
            font=("Segoe UI", 7, "italic"), anchor="w"
        ).grid(row=8, column=0, sticky="w", padx=16)

        # Action buttons
        btn_frame = tk.Frame(form, bg=self.C_PANEL)
        btn_frame.grid(row=9, column=0, pady=12, padx=14, sticky="w")

        for label, cmd, color in [
            ("Create",  self._create_reservation,  self.C_ACCENT),
            ("Confirm", self._confirm_reservation,  "#16a34a"),
            ("Process", self._process_reservation,  "#0284c7"),
            ("Cancel",  self._cancel_reservation,   "#dc2626"),
        ]:
            self._btn(btn_frame, label, cmd, color=color, width=9).pack(
                side="left", padx=3
            )

        # Right — reservations list
        right_wrap = tk.Frame(wrapper, bg=self.C_BG)
        right_wrap.pack(side="right", fill="both", expand=True)

        list_frame = self._section(
            right_wrap, "System Reservations",
            side="top", fill="both", expand=True
        )
        self._reservations_box = tk.Listbox(
            list_frame,
            bg=self.C_INPUT,
            fg=self.C_TEXT,
            font=("Consolas", 9),
            relief="flat",
            selectbackground=self.C_ACCENT,
            activestyle="none"
        )
        self._reservations_box.pack(fill="both", expand=True, padx=8, pady=8)

        self._res_count = tk.StringVar(value="Total: 0 reservations")
        tk.Label(
            right_wrap,
            textvariable=self._res_count,
            bg=self.C_BG,
            fg=self.C_HINT,
            font=("Segoe UI", 8)
        ).pack(anchor="e", padx=8)

    def _create_reservation(self) -> None:
        try:
            idx_c = self._combo_client.current()
            idx_s = self._combo_service.current()
            if idx_c < 0 or idx_s < 0:
                messagebox.showwarning(
                    "Missing Data",
                    "Please select both a client and a service."
                )
                return
            duration = self._gui_validate_duration(self._entry_duration.get())
            client  = self._clients[idx_c]
            service = self._services[idx_s]

            reservation = Reserva(
                cliente=client,
                servicio=service,
                duracion=duration
            )
            self._reservations.append(reservation)
            self._refresh_reservations()
            self._res_count.set(
                f"Total: {len(self._reservations)} reservation(s)"
            )
            self._status(f"Reservation #{reservation.id} created.")
            self._logger.info(f"GUI: Reservation created -> {reservation}")
            messagebox.showinfo("Reservation Created", str(reservation))

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            self._logger.error(f"GUI: Input error creating reservation -> {e}")
        except ErrorSistema as e:
            messagebox.showerror("Reservation Error", str(e))
            self._logger.error(f"GUI: Error creating reservation -> {e}")

    def _selected_reservation(self):
        sel = self._reservations_box.curselection()
        if not sel:
            messagebox.showwarning(
                "No Selection",
                "Please select a reservation from the list first."
            )
            return None
        return self._reservations[sel[0]]

    def _confirm_reservation(self) -> None:
        r = self._selected_reservation()
        if not r:
            return
        try:
            msg = r.confirmar()
            self._refresh_reservations()
            self._status(f"Reservation #{r.id} confirmed.")
            messagebox.showinfo("Confirmed", msg)
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e))
            self._logger.error(f"GUI: Error confirming reservation -> {e}")

    def _process_reservation(self) -> None:
        r = self._selected_reservation()
        if not r:
            return
        try:
            msg = r.procesar()
            self._refresh_reservations()
            self._status(f"Reservation #{r.id} processed.")
            messagebox.showinfo("Processed", msg)
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e))
            self._logger.error(f"GUI: Error processing reservation -> {e}")

    def _cancel_reservation(self) -> None:
        r = self._selected_reservation()
        if not r:
            return
        try:
            msg = r.cancelar("Cancelled from the interface")
            self._refresh_reservations()
            self._status(f"Reservation #{r.id} cancelled.")
            messagebox.showinfo("Cancelled", msg)
        except ErrorSistema as e:
            messagebox.showerror("Error", str(e))
            self._logger.error(f"GUI: Error cancelling reservation -> {e}")

    def _refresh_reservations(self) -> None:
        self._reservations_box.delete(0, tk.END)
        for r in self._reservations:
            self._reservations_box.insert(tk.END, f"  {r}")

    #  TAB 4 — SYSTEM LOGS

    def _tab_logs(self, nb: ttk.Notebook) -> None:
        outer = ttk.Frame(nb)
        nb.add(outer, text="System Logs")

        # Toolbar
        toolbar = tk.Frame(outer, bg=self.C_PANEL, height=44)
        toolbar.pack(fill="x", padx=10, pady=(10, 0))
        toolbar.pack_propagate(False)

        tk.Label(
            toolbar,
            text="Source file:  logs/sistema.log",
            bg=self.C_PANEL,
            fg=self.C_HINT,
            font=("Segoe UI", 8)
        ).pack(side="left", padx=12, pady=10)

        self._btn(
            toolbar, "Refresh Logs", self._load_logs,
            color=self.C_ACCENT, width=14
        ).pack(side="right", padx=10, pady=8)

        # Color legend
        legend_frame = tk.Frame(outer, bg=self.C_BG)
        legend_frame.pack(fill="x", padx=10, pady=6)

        tk.Label(
            legend_frame,
            text="Log levels:",
            bg=self.C_BG,
            fg=self.C_HINT,
            font=("Segoe UI", 8, "bold")
        ).pack(side="left", padx=(4, 8))

        for label, color in [
            ("INFO",     "#22c55e"),
            ("WARNING",  "#f59e0b"),
            ("ERROR",    "#ef4444"),
            ("CRITICAL", "#dc2626"),
        ]:
            tk.Label(
                legend_frame,
                text=f"  {label}  ",
                bg=color,
                fg="white",
                font=("Segoe UI", 8, "bold"),
                padx=6,
                pady=2
            ).pack(side="left", padx=4)

        # Log text area
        log_border = tk.Frame(
            outer, bg=self.C_BORDER, bd=1, relief="groove"
        )
        log_border.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._log_area = scrolledtext.ScrolledText(
            log_border,
            bg="#0d0d1a",
            fg=self.C_TEXT,
            font=("Consolas", 9),
            relief="flat",
            state="disabled",
            wrap="none",
            padx=10,
            pady=6
        )
        self._log_area.pack(fill="both", expand=True)

        self._log_area.tag_configure("INFO",     foreground="#22c55e")
        self._log_area.tag_configure("WARNING",  foreground="#f59e0b")
        self._log_area.tag_configure("ERROR",    foreground="#ef4444")
        self._log_area.tag_configure("CRITICAL", foreground="#dc2626")
        self._log_area.tag_configure("SEPARATOR",foreground="#4c4c6e")
        self._log_area.tag_configure("DEFAULT",  foreground="#64748b")

        self._load_logs()

    def _load_logs(self) -> None:
        self._log_area.configure(state="normal")
        self._log_area.delete("1.0", tk.END)
        try:
            with open("logs/sistema.log", "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    self._log_area.insert(tk.END, "\n", "DEFAULT")
                    continue
                if set(stripped) <= {"=", "-", " "}:
                    self._log_area.insert(tk.END, line, "SEPARATOR")
                    continue
                if "| INFO" in line:
                    tag = "INFO"
                elif "| WARNING" in line:
                    tag = "WARNING"
                elif "| ERROR" in line:
                    tag = "ERROR"
                elif "| CRITICAL" in line:
                    tag = "CRITICAL"
                else:
                    tag = "DEFAULT"
                self._log_area.insert(tk.END, line, tag)

        except FileNotFoundError:
            self._log_area.insert(
                tk.END,
                "No log file found yet.\n"
                "Run the system to generate log entries.\n",
                "DEFAULT"
            )

        self._log_area.configure(state="disabled")
        self._log_area.see(tk.END)
        self._status("Logs refreshed successfully.")