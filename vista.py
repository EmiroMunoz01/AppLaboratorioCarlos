import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import modelo


class VistaPrincipal:
    def __init__(self, root):
        self.root = root
        # …
        modelo.initialize_db()
        self.crear_interfaz()  # esto define propietario_combo
        self.cargar_usuarios()  # usa tree_usuarios
        self.cargar_vehiculos()  # usa tree_vehiculos
        self.cargar_propietarios()  # ahora propietario_combo ya existe

    def cargar_datos_iniciales(self):
        self.cargar_usuarios()
        self.cargar_vehiculos()

    def crear_interfaz(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # CREAR FRAMES
        self.frame_usuarios = ttk.Frame(self.notebook)
        self.frame_vehiculos = ttk.Frame(self.notebook)
        self.frame_consultas = ttk.Frame(self.notebook)

        # AGREGAR PESTAÑAS
        self.notebook.add(self.frame_usuarios, text="👤 Usuarios")
        self.notebook.add(self.frame_vehiculos, text="🚗 Vehículos")
        self.notebook.add(self.frame_consultas, text="📊 Consultas")

        # CREAR CONTENIDO DE CADA PESTAÑA
        self.crear_pestaña_usuarios()
        self.crear_pestaña_vehiculos()  # Aquí se define propietario_combo
        self.crear_pestaña_consultas()

    def _parse_money(self, s):
        s = str(s).strip()
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s and "." not in s:
            s = s.replace(",", ".")
        return float(s)

    def _fmt_money(self, n):
        return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def crear_pestaña_usuarios(self):
        main = ttk.Frame(self.frame_usuarios)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        left = ttk.LabelFrame(main, text="Datos del Usuario", padding=15)
        left.pack(side="left", fill="y", padx=(0, 10))
        ttk.Label(left, text="Cédula:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.cedula_entry = ttk.Entry(left)
        self.cedula_entry.grid(row=1, column=0, pady=(0, 10))
        ttk.Label(left, text="Nombre:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.nombre_entry = ttk.Entry(left)
        self.nombre_entry.grid(row=3, column=0, pady=(0, 10))
        ttk.Label(left, text="Apellido:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky="w", pady=5
        )
        self.apellido_entry = ttk.Entry(left)
        self.apellido_entry.grid(row=5, column=0, pady=(0, 10))
        ttk.Label(left, text="Teléfono:", font=("Arial", 10, "bold")).grid(
            row=6, column=0, sticky="w", pady=5
        )
        self.telefono_entry = ttk.Entry(left)
        self.telefono_entry.grid(row=7, column=0, pady=(0, 10))
        ttk.Label(left, text="Dirección:", font=("Arial", 10, "bold")).grid(
            row=8, column=0, sticky="w", pady=5
        )
        self.dir_entry = ttk.Entry(left)
        self.dir_entry.grid(row=9, column=0, pady=(0, 15))
        btns = ttk.Frame(left)
        btns.grid(row=10, column=0, pady=10)
        ttk.Button(btns, text="💾 Guardar", command=self.guardar_usuario).pack(pady=2)
        ttk.Button(btns, text="✏️ Actualizar", command=self.actualizar_usuario).pack(
            pady=2
        )
        ttk.Button(btns, text="🗑️ Eliminar", command=self.eliminar_usuario).pack(pady=2)
        ttk.Button(btns, text="🆕 Nuevo", command=self.limpiar_usuario).pack(pady=2)
        right = ttk.LabelFrame(main, text="Lista de Usuarios", padding=10)
        right.pack(side="right", fill="both", expand=True)
        cols_usr = ("Cédula", "Nombre", "Apellido", "Teléfono", "Dirección")
        self.tree_usuarios = ttk.Treeview(
            right, columns=cols_usr, show="headings", height=20
        )
        for c in cols_usr:
            self.tree_usuarios.heading(c, text=c)
            self.tree_usuarios.column(c, width=120)
        sb = ttk.Scrollbar(right, orient="vertical", command=self.tree_usuarios.yview)
        self.tree_usuarios.configure(yscrollcommand=sb.set)
        self.tree_usuarios.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_usuarios.bind("<<TreeviewSelect>>", self.seleccionar_usuario)

        self.usr_pagina = 0
        self.usr_page_size = 30

        def recargar_usuarios():
            offset = self.usr_pagina * self.usr_page_size
            rows = modelo.listar_usuarios_paginados(
                limit=self.usr_page_size, offset=offset
            )
            self.tree_usuarios.delete(*self.tree_usuarios.get_children())
            for usr in rows:
                self.tree_usuarios.insert("", "end", iid=str(usr[0]), values=usr[1:])
            total = modelo.contar_usuarios()
            desde = offset + 1 if total > 0 else 0
            hasta = min(offset + self.usr_page_size, total)
            usr_label.config(text=f"{desde}-{hasta} de {total}")

        # Etiqueta de página y botones
        usr_label = ttk.Label(left, text="")
        usr_label.grid(row=11, column=0, pady=(0, 10))
        nav = ttk.Frame(left)
        nav.grid(row=12, column=0)
        ttk.Button(
            nav, text="◀", command=lambda: (self._usr_anterior(), recargar_usuarios())
        ).pack(side="left")
        ttk.Button(
            nav, text="▶", command=lambda: (self._usr_siguiente(), recargar_usuarios())
        ).pack(side="left")

        recargar_usuarios()

    def crear_pestaña_vehiculos(self):
        # Contenedor principal
        main = ttk.Frame(self.frame_vehiculos)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        left = ttk.LabelFrame(main, text="Datos del Vehículo", padding=15)
        left.pack(side="left", fill="y", padx=(0, 10))

        # Campos de entrada
        ttk.Label(left, text="Placa:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.placa_entry = ttk.Entry(left)
        self.placa_entry.grid(row=1, column=0, pady=(0, 10))

        ttk.Label(left, text="Motor:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.motor_entry = ttk.Entry(left)
        self.motor_entry.grid(row=3, column=0, pady=(0, 10))

        ttk.Label(left, text="Marca:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky="w", pady=5
        )
        self.marca_entry = ttk.Entry(left)
        self.marca_entry.grid(row=5, column=0, pady=(0, 10))

        ttk.Label(left, text="Fecha Entrada:", font=("Arial", 10, "bold")).grid(
            row=6, column=0, sticky="w", pady=5
        )
        self.fecha_entry = DateEntry(left, date_pattern="yyyy-MM-dd")
        self.fecha_entry.grid(row=7, column=0, pady=(0, 10))

        ttk.Label(left, text="Fecha Salida:", font=("Arial", 10, "bold")).grid(
            row=8, column=0, sticky="w", pady=5
        )
        self.fecha_salida_entry = DateEntry(left, date_pattern="yyyy-MM-dd")
        self.fecha_salida_entry.grid(row=9, column=0, pady=(0, 15))
        self.fecha_salida_entry.delete(0, tk.END)

            # Combobox de propietarios con mapeo interno
        ttk.Label(left, text="Propietario:", font=("Arial",10,"bold")).grid(
            row=10, column=0, sticky="w", pady=5
        )
        self.propietario_combo = ttk.Combobox(left, state="readonly")
        
        usuarios = modelo.listar_usuarios()
        vals = [f"{u[1]} – {u[2]} {u[3]}".strip() for u in usuarios]
        self.propietario_combo["values"] = vals
        if vals:
            self.propietario_combo.current(0)
                
                
        
        self.propietario_combo.grid(row=11, column=0, pady=(0,15))







        # Construye los mapas y llena el combobox inmediatamente
        usuarios = modelo.listar_usuarios()
        self.map_cedula_a_id     = { str(u[1]): u[0] for u in usuarios }
        self.map_cedula_a_nombre = { str(u[1]): u[2] for u in usuarios }
        vals = [ f"{u[1]} - {u[2]}" for u in usuarios ]
        self.propietario_combo["values"] = vals

        # Botones de acción
        btns = ttk.Frame(left)
        btns.grid(row=12, column=0, pady=10)
        ttk.Button(btns, text="💾 Guardar", command=self.guardar_vehiculo).pack(pady=2)
        ttk.Button(btns, text="✏️ Actualizar", command=self.actualizar_vehiculo).pack(
            pady=2
        )
        ttk.Button(btns, text="🗑️ Eliminar", command=self.eliminar_vehiculo).pack(pady=2)
        ttk.Button(btns, text="🆕 Nuevo", command=self.limpiar_vehiculo).pack(pady=2)
        ttk.Button(
            btns,
            text="🔄 Recargar",
            command=lambda: self.propietario_combo.configure(
                values=[f"{u[1]} - {u[2]}" for u in modelo.listar_usuarios()]
            ),
        ).pack(pady=2)

        ttk.Button(btns, text="🧾 Cotización", command=self.abrir_cotizacion).pack(
            pady=2
        )
        ttk.Button(
            btns,
            text="🗂 Historial cotizaciones",
            command=self.abrir_historial_cotizaciones,
        ).pack(pady=2)
        ttk.Button(btns, text="📝 Acta garantía", command=self.abrir_acta).pack(pady=2)
        ttk.Button(
            btns, text="📄 Historial actas", command=self.abrir_historial_actas
        ).pack(pady=2)

        # Treeview de vehículos
        right = ttk.LabelFrame(main, text="Lista de Vehículos", padding=10)
        right.pack(side="right", fill="both", expand=True)
        cols = (
            "Placa",
            "Motor",
            "Marca",
            "Fecha Entrada",
            "Fecha Salida",
            "Propietario",
            "Teléfono",
        )
        self.tree_vehiculos = ttk.Treeview(
            right, columns=cols, show="headings", height=25
        )
        for c in cols:
            self.tree_vehiculos.heading(c, text=c)
            self.tree_vehiculos.column(c, width=120)
        sb = ttk.Scrollbar(right, orient="vertical", command=self.tree_vehiculos.yview)
        self.tree_vehiculos.configure(yscrollcommand=sb.set)
        self.tree_vehiculos.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_vehiculos.bind("<<TreeviewSelect>>", self.seleccionar_vehiculo)

        # Configurar paginación en el panel izquierdo
        self.configurar_paginacion_vehiculos(left)

        # Carga inicial de datos
        self.cargar_vehiculos()

    def crear_pestaña_consultas(self):
        # Contenedor principal
        main = ttk.Frame(self.frame_consultas)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # Título de la consulta
        ttk.Label(
            main, text="Vehículos por Propietario", font=("Arial", 12, "bold")
        ).pack(anchor="w")

        # Combobox para seleccionar propietario
        self.consulta_combo = ttk.Combobox(main, state="readonly")
        self.consulta_combo.pack(anchor="w", pady=5)

        # Botón de consulta
        ttk.Button(
            main, text="🔍 Consultar", command=self.consultar_vehiculos_usuario
        ).pack(anchor="w", pady=5)

        # Treeview para mostrar resultados
        cols = ("Placa", "Motor", "Marca")
        self.tree_resultado = ttk.Treeview(
            main, columns=cols, show="headings", height=10
        )
        for c in cols:
            self.tree_resultado.heading(c, text=c)
            self.tree_resultado.column(c, width=120)
        sb2 = ttk.Scrollbar(main, orient="vertical", command=self.tree_resultado.yview)
        self.tree_resultado.configure(yscrollcommand=sb2.set)
        self.tree_resultado.pack(fill="both", expand=True)
        sb2.pack(side="right", fill="y")

    # ===== BÚSQUEDA POR PLACA =====
    def abrir_busqueda_por_placa(self):
        win = tk.Toplevel(self.root)
        win.title("Buscar vehículos por placa")
        win.transient(self.root)
        win.grab_set()
        win.geometry("650x420")
        cont = ttk.Frame(win, padding=10)
        cont.pack(fill="both", expand=True)
        fila = ttk.Frame(cont)
        fila.pack(fill="x", pady=(0, 8))
        ttk.Label(fila, text="Placa:").pack(side="left")
        placa_entry = ttk.Entry(fila, width=18)
        placa_entry.pack(side="left", padx=6)
        ttk.Button(
            fila,
            text="Buscar",
            command=lambda: self._buscar_y_listar_por_placa(
                win, placa_entry.get().strip().upper()
            ),
        ).pack(side="left")
        ttk.Button(fila, text="Cerrar", command=win.destroy).pack(side="right")
        cols = (
            "Placa",
            "Motor",
            "Marca",
            "Fecha Entrada",
            "Fecha Salida",
            "Cédula",
            "Teléfono",
        )
        tree = ttk.Treeview(cont, columns=cols, show="headings", height=14)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=110)
        sb = ttk.Scrollbar(cont, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        win.tree_result = tree
        win.placa_entry = placa_entry
        placa_entry.bind(
            "<Return>",
            lambda _e: self._buscar_y_listar_por_placa(
                win, placa_entry.get().strip().upper()
            ),
        )

        def on_dclick(_):
            sel = tree.selection()
            if not sel:
                return
            placa, motor, marca, fe, fs, ced, tel = tree.item(sel[0])["values"]
            self.placa_original = placa
            self.placa_entry.config(state="normal")
            self.placa_entry.delete(0, tk.END)
            self.placa_entry.insert(0, placa)
            self.placa_entry.config(state="disabled")
            self.motor_entry.delete(0, tk.END)
            self.motor_entry.insert(0, motor)
            self.marca_entry.delete(0, tk.END)
            self.marca_entry.insert(0, marca)
            self.fecha_entry.set_date(fe)
            if fs and fs != "None":
                self.fecha_salida_entry.set_date(fs)
            else:
                self.fecha_salida_entry.delete(0, tk.END)
            nombre = self.map_cedula_a_nombre.get(str(ced), "")
            self.propietario_combo.set(f"{ced} - {nombre}" if nombre else str(ced))
            win.destroy()

        tree.bind("<Double-1>", on_dclick)
        self._buscar_y_listar_por_placa(win, "")

    def _buscar_y_listar_por_placa(self, win, texto):
        rows = modelo.listar_vehiculos()
        t = (texto or "").upper()
        filtradas = [r for r in rows if t in r[0].upper()] if t else rows
        tree = win.tree_result
        for i in tree.get_children():
            tree.delete(i)
        for placa, motor, marca, fe, fs, ced, tel in filtradas:
            tree.insert("", "end", values=(placa, motor, marca, fe, fs, ced, tel))
        if not filtradas and t:
            messagebox.showinfo("Resultado", "No se encontraron placas que coincidan")

    # ===== COTIZACIÓN =====
    def abrir_cotizacion(self):
        placa = self.placa_entry.get().strip().upper()
        if not placa:
            messagebox.showwarning(
                "Aviso", "Ingrese o seleccione una placa antes de crear la cotización"
            )
            return
        win = tk.Toplevel(self.root)
        win.title(f"Cotización - {placa}")
        win.transient(self.root)
        win.grab_set()
        win.geometry("920x520")
        cont = ttk.Frame(win, padding=10)
        cont.pack(fill="both", expand=True)
        top = ttk.Frame(cont)
        top.pack(fill="x")
        ttk.Label(top, text=f"Placa: {placa}", font=("Arial", 10, "bold")).pack(
            side="left"
        )
        ttk.Label(top, text="  |  Fecha:", font=("Arial", 10)).pack(
            side="left", padx=(8, 2)
        )
        ttk.Label(top, text=self.fecha_entry.get_date().strftime("%Y-%m-%d")).pack(
            side="left"
        )
        form = ttk.LabelFrame(cont, text="Agregar ítem", padding=8)
        form.pack(fill="x", pady=(10, 6))
        ttk.Label(form, text="Artículo #").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Descripción").grid(row=0, column=1, sticky="w")
        ttk.Label(form, text="Cant").grid(row=0, column=2, sticky="w")
        ttk.Label(form, text="P/U").grid(row=0, column=3, sticky="w")
        art_entry = ttk.Entry(form, width=16)
        art_entry.grid(row=1, column=0, padx=4)
        desc_entry = ttk.Entry(form, width=48)
        desc_entry.grid(row=1, column=1, padx=4)
        cant_entry = ttk.Entry(form, width=8)
        cant_entry.grid(row=1, column=2, padx=4)
        pu_entry = ttk.Entry(form, width=10)
        pu_entry.grid(row=1, column=3, padx=4)

        def add_item():
            try:
                art = art_entry.get().strip()
                desc = desc_entry.get().strip()
                cant = self._parse_money(cant_entry.get())
                pu = self._parse_money(pu_entry.get())
                total = cant * pu
                if not desc:
                    raise ValueError("Descripción requerida")
                win.tree.insert(
                    "",
                    "end",
                    values=(
                        art,
                        desc,
                        f"{cant:g}",
                        self._fmt_money(pu),
                        self._fmt_money(total),
                    ),
                )
                art_entry.delete(0, tk.END)
                desc_entry.delete(0, tk.END)
                cant_entry.delete(0, tk.END)
                pu_entry.delete(0, tk.END)
                _recalc_total()
            except Exception as e:
                messagebox.showerror("Error", f"Dato inválido: {e}")

        ttk.Button(form, text="Agregar", command=add_item).grid(row=1, column=4, padx=6)
        pu_entry.bind("<Return>", lambda e: add_item())
        cols = ("Articulo", "Descripción", "Cant", "P/U", "Total")
        tree = ttk.Treeview(cont, columns=cols, show="headings", height=12)
        for c, w in zip(cols, (120, 420, 80, 100, 120)):
            tree.heading(c, text=c)
            tree.column(
                c, width=w, anchor="e" if c in ("Cant", "P/U", "Total") else "w"
            )
        sb = ttk.Scrollbar(cont, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        win.tree = tree
        actions = ttk.Frame(cont)
        actions.pack(fill="x", pady=(8, 0))

        def delete_sel():
            sel = tree.selection()
            if not sel:
                return
            for i in sel:
                tree.delete(i)
            _recalc_total()

        ttk.Button(actions, text="Eliminar seleccionado", command=delete_sel).pack(
            side="left"
        )
        totals = ttk.Frame(cont)
        totals.pack(fill="x", pady=(8, 0))
        ttk.Label(totals, text="Total:").pack(side="right")
        total_var = tk.StringVar(value="0,00")
        ttk.Label(
            totals,
            textvariable=total_var,
            width=12,
            anchor="e",
            font=("Arial", 10, "bold"),
        ).pack(side="right")

        def _recalc_total():
            total = 0.0
            for iid in tree.get_children():
                tot_s = tree.item(iid)["values"][4]
                total += self._parse_money(tot_s)
            total_var.set(self._fmt_money(total))

        bottom = ttk.Frame(cont)
        bottom.pack(fill="x", pady=(10, 0))

        def guardar_persistente():
            try:
                items = []
                total = 0.0
                for iid in win.tree.get_children():
                    art, desc, cant_s, pu_s, tot_s = win.tree.item(iid)["values"]
                    cant = self._parse_money(cant_s)
                    pu = self._parse_money(pu_s)
                    tot = self._parse_money(tot_s)
                    items.append(
                        {
                            "articulo": str(art) or None,
                            "descripcion": str(desc),
                            "cantidad": cant,
                            "precio_unit": pu,
                            "total": tot,
                        }
                    )
                    total += tot
                if not items:
                    messagebox.showwarning("Aviso", "Agregue al menos un ítem")
                    return
                placa = self.placa_entry.get().strip().upper()
                if not placa:
                    messagebox.showwarning(
                        "Aviso", "Ingrese/seleccione una placa válida"
                    )
                    return
                fecha = self.fecha_entry.get_date().strftime("%Y-%m-%d")
                cot_id = modelo.guardar_cotizacion(placa, fecha, round(total, 2), items)
                messagebox.showinfo(
                    "Cotización",
                    f"Cotización guardada (ID {cot_id}) para placa {placa}",
                )
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")

        ttk.Button(bottom, text="Guardar", command=guardar_persistente).pack(
            side="left"
        )
        ttk.Button(bottom, text="Cerrar", command=win.destroy).pack(side="right")

    # ===== HISTORIAL COTIZACIONES =====
    def abrir_historial_cotizaciones(self):
        placa = self.placa_entry.get().strip().upper()
        if not placa:
            messagebox.showwarning("Aviso", "Ingrese/seleccione una placa")
            return
        win = tk.Toplevel(self.root)
        win.title(f"Historial - {placa}")
        win.geometry("520x420")
        win.transient(self.root)
        win.grab_set()
        top = ttk.Frame(win)
        top.pack(fill="both", expand=True, padx=10, pady=(10, 4))
        cols = ("ID", "Fecha", "Total")
        win.tree = ttk.Treeview(top, columns=cols, show="headings", height=14)
        for c in cols:
            win.tree.heading(c, text=c)
            w = 100 if c != "Fecha" else 160
            win.tree.column(c, width=w, anchor="e" if c != "Fecha" else "center")
        sb = ttk.Scrollbar(top, orient="vertical", command=win.tree.yview)
        win.tree.configure(yscrollcommand=sb.set)
        win.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def recargar():
            for i in win.tree.get_children():
                win.tree.delete(i)
            for cid, f, t in modelo.listar_cotizaciones_por_placa(placa):
                win.tree.insert("", "end", values=(cid, f, f"{t:,.2f}"))

        def eliminar_sel():
            sel = win.tree.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Seleccione una cotización")
                return
            cid = win.tree.item(sel[0])["values"][0]
            if not messagebox.askyesno("Confirmar", f"¿Eliminar cotización ID {cid}?"):
                return
            ok = modelo.eliminar_cotizacion(int(cid))
            if ok:
                win.tree.delete(sel[0])
                messagebox.showinfo("Éxito", "Cotización eliminada")
            else:
                messagebox.showwarning("Aviso", "No se pudo eliminar")

        recargar()
        actions = ttk.Frame(win)
        actions.pack(fill="x", padx=10, pady=(4, 10))
        ttk.Button(actions, text="Eliminar seleccionada", command=eliminar_sel).pack(
            side="left"
        )
        ttk.Button(actions, text="Recargar", command=recargar).pack(side="left", padx=6)
        ttk.Button(actions, text="Cerrar", command=win.destroy).pack(side="right")



    # ===== ACTAS GARANTÍA =====
    def abrir_acta(self):
        placa = self.placa_entry.get().strip().upper()
        if not placa:
            messagebox.showwarning("Aviso", "Seleccione una placa")
            return
        if not messagebox.askyesno("Confirmar", f"Generar Acta de garantía para {placa}?"):
            return
        try:
            from imprimir_acta import generar_acta_para_placa

            # Llamada sin 'fecha_elaboracion'
            acta_id, docx, pdf = generar_acta_para_placa(
                placa,
                creado_por="operador"
            )
            texto = f"Acta ID {acta_id} creada.\nDOCX: {docx}"
            if pdf:
                texto += f"\nPDF: {pdf}"
            messagebox.showinfo("Éxito", texto)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el acta: {e}")

    def abrir_historial_actas(self):
        placa = self.placa_entry.get().strip().upper()
        if not placa:
            messagebox.showwarning("Aviso", "Seleccione una placa")
            return
        win = tk.Toplevel(self.root)
        win.title(f"Actas - {placa}")
        win.geometry("720x420")
        win.transient(self.root)
        win.grab_set()
        cols = ("ID", "Fecha", "DOCX", "PDF", "Obs")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=14)
        for c, w in zip(cols, (60, 100, 260, 160, 220)):
            tree.heading(c, text=c)
            tree.column(c, width=w)
        sb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def recargar():
            for i in tree.get_children():
                tree.delete(i)
            for id_, f, docx, pdf, obs in modelo.listar_actas_por_placa(placa):
                tree.insert("", "end", values=(id_, str(f), docx, pdf or "", obs or ""))

        recargar()
        barra = ttk.Frame(win)
        barra.pack(fill="x", pady=6)

        def abrir_docx():
            sel = tree.selection()
            if not sel:
                return
            path = tree.item(sel[0])["values"][2]
            try:
                os.startfile(path)
            except Exception as e:
                messagebox.showerror("Abrir DOCX", str(e))

        def imprimir_acta():
            sel = tree.selection()
            if not sel:
                return
            path = tree.item(sel[0])["values"][3] or tree.item(sel[0])["values"][2]
            if not path:
                messagebox.showwarning("Imprimir", "No hay archivo para imprimir")
                return
            try:
                os.startfile(path, "print")
            except Exception as e:
                messagebox.showerror("Imprimir", f"No se pudo imprimir:\n{e}")

        ttk.Button(barra, text="Abrir DOCX", command=abrir_docx).pack(side="left")
        ttk.Button(barra, text="Imprimir", command=imprimir_acta).pack(
            side="left", padx=6
        )
        ttk.Button(barra, text="Recargar", command=recargar).pack(side="left", padx=6)
        ttk.Button(barra, text="Cerrar", command=win.destroy).pack(side="right")

    # ===== CRUD USUARIOS =====
    def seleccionar_usuario(self, _):
        sel = self.tree_usuarios.selection()
        if not sel:
            return
        self.usuario_id_sel = int(sel[0])
        ced, nom, ape, tel, dire = self.tree_usuarios.item(sel[0])["values"]
        self.cedula_entry.delete(0, tk.END)
        self.cedula_entry.insert(0, ced)
        self.nombre_entry.delete(0, tk.END)
        self.nombre_entry.insert(0, nom)
        self.apellido_entry.delete(0, tk.END)
        self.apellido_entry.insert(0, ape)
        self.telefono_entry.delete(0, tk.END)
        self.telefono_entry.insert(0, tel)
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, dire or "")

    def guardar_usuario(self):
        try:
            ced = int(self.cedula_entry.get().strip())
            nom = self.nombre_entry.get().strip()
            ape = self.apellido_entry.get().strip()
            tel = self.telefono_entry.get().strip()
            dire = self.dir_entry.get().strip() or None
            modelo.guardar_usuario(ced, nom, ape, tel, dire)
            messagebox.showinfo("Éxito", "Usuario guardado")
            self.cargar_usuarios()
            self.cargar_propietarios()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_usuario(self):
        try:
            if not self.usuario_id_sel:
                messagebox.showwarning("Aviso", "Seleccione un usuario de la lista")
                return
            nueva_ced = int(self.cedula_entry.get().strip())
            nom = self.nombre_entry.get().strip()
            ape = self.apellido_entry.get().strip()
            tel = self.telefono_entry.get().strip()
            dire = self.dir_entry.get().strip() or None
            ok = modelo.actualizar_usuario(
                self.usuario_id_sel, nueva_ced, nom, ape, tel, dire
            )
            messagebox.showinfo("Éxito", "Usuario actualizado" if ok else "Sin cambios")
            self.cargar_usuarios()
            self.cargar_propietarios()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_usuario(self):
        sel = self.tree_usuarios.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un usuario")
            return
        user_id = int(sel[0])
        ok = modelo.eliminar_usuario(user_id)
        if ok:
            messagebox.showinfo("Éxito", "Usuario eliminado")
            self.tree_usuarios.delete(sel[0])
            self.limpiar_usuario()
            self.cargar_propietarios()
        else:
            messagebox.showwarning("Aviso", "No se pudo eliminar")

    def limpiar_usuario(self):
        self.usuario_id_sel = None
        self.cedula_entry.delete(0, tk.END)
        self.nombre_entry.delete(0, tk.END)
        self.apellido_entry.delete(0, tk.END)
        self.telefono_entry.delete(0, tk.END)
        self.dir_entry.delete(0, tk.END)

    def cargar_usuarios(self):
        for i in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(i)
        for usr in modelo.listar_usuarios():
            self.tree_usuarios.insert("", "end", iid=str(usr[0]), values=usr[1:])

    # ===== CRUD VEHÍCULOS =====
    def seleccionar_vehiculo(self, _):
        sel = self.tree_vehiculos.selection()
        if not sel:
            return
        placa, motor, marca, fe, fs, ced, tel = self.tree_vehiculos.item(sel[0])[
            "values"
        ]
        self.placa_original = placa
        self.placa_entry.config(state="normal")
        self.placa_entry.delete(0, tk.END)
        self.placa_entry.insert(0, placa)
        self.placa_entry.config(state="disabled")
        self.motor_entry.delete(0, tk.END)
        self.motor_entry.insert(0, motor)
        self.marca_entry.delete(0, tk.END)
        self.marca_entry.insert(0, marca)
        self.fecha_entry.set_date(fe)
        if fs and fs != "None":
            self.fecha_salida_entry.set_date(fs)
        else:
            self.fecha_salida_entry.delete(0, tk.END)
        nombre = self.map_cedula_a_nombre.get(str(ced), "")
        self.propietario_combo.set(f"{ced} - {nombre}" if nombre else str(ced))

    def guardar_vehiculo(self):
        try:
            placa = self.placa_entry.get().strip().upper()
            if not placa:
                messagebox.showwarning("Aviso", "La placa es obligatoria")
                return

            # Validar existencia previa
            todos = [
                row[0] for row in modelo.listar_vehiculos()
            ]  # lista de placas existentes
            if placa in todos:
                messagebox.showwarning("Aviso", f"La placa {placa} ya existe")
                return

            motor = self.motor_entry.get().strip()
            marca = self.marca_entry.get().strip()
            fe = self.fecha_entry.get_date().strftime("%Y-%m-%d")
            fs_text = self.fecha_salida_entry.get().strip()
            fs = fs_text if fs_text else None
            uid = None
            if self.propietario_combo.get().strip():
                ced = self.propietario_combo.get().split(" - ")[0].strip()
                uid = self.map_cedula_a_id.get(ced)

            # Inserción única
            modelo.guardar_vehiculo(placa, motor, marca, fe, fs, uid)
            messagebox.showinfo("Éxito", "Vehículo guardado")

            # Recarga y limpieza de duplicados en UI
            self.cargar_vehiculos()
            self.placa_original = placa

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_vehiculo(self):
        try:
            if not self.placa_original:
                messagebox.showwarning(
                    "Aviso", "Seleccione un vehículo de la lista para actualizar"
                )
                return
            motor = self.motor_entry.get().strip()
            marca = self.marca_entry.get().strip()
            fe = self.fecha_entry.get_date().strftime("%Y-%m-%d")
            fs_text = self.fecha_salida_entry.get().strip()
            fs = fs_text if fs_text else None
            uid = None
            if self.propietario_combo.get().strip():
                ced = self.propietario_combo.get().split(" - ")[0].strip()
                uid = self.map_cedula_a_id.get(ced)
            ok = modelo.actualizar_vehiculo(
                self.placa_original, motor, marca, fe, fs, uid
            )
            messagebox.showinfo(
                "Éxito", "Vehículo actualizado" if ok else "Sin cambios"
            )
            self.cargar_vehiculos()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_vehiculo(self):
        sel = self.tree_vehiculos.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un vehículo")
            return
        placa = self.tree_vehiculos.item(sel[0])["values"][0]
        ok = modelo.eliminar_vehiculo(placa)
        if ok:
            messagebox.showinfo("Éxito", "Vehículo eliminado")
            self.tree_vehiculos.delete(sel[0])
            self.limpiar_vehiculo()
        else:
            messagebox.showwarning("Aviso", "No se pudo eliminar")

    def limpiar_vehiculo(self):
        self.placa_entry.config(state="normal")
        self.placa_entry.delete(0, tk.END)
        self.motor_entry.delete(0, tk.END)
        self.marca_entry.delete(0, tk.END)
        self.propietario_combo.set("")
        self.fecha_entry.delete(0, tk.END)
        self.fecha_salida_entry.delete(0, tk.END)
        self.placa_original = None

    def cargar_propietarios(self):
        usuarios = modelo.listar_usuarios()
        vals = [f"{u[1]} - {u[2]}" for u in usuarios]
        self.consulta_combo["values"] = vals

    def limpiar_vehiculo(self):
        self.placa_entry.config(state="normal")
        self.placa_entry.delete(0, tk.END)
        self.motor_entry.delete(0, tk.END)
        self.marca_entry.delete(0, tk.END)
        self.propietario_combo.set("")
        self.fecha_entry.delete(0, tk.END)
        self.fecha_salida_entry.delete(0, tk.END)
        self.placa_original = None

    def cargar_vehiculos(self):
        """
        Recarga la lista de vehículos usando paginación desde el modelo.
        """
        # Limpia los ítems viejos
        self.tree_vehiculos.delete(*self.tree_vehiculos.get_children())

        # Calcula offset y obtiene la página actual
        offset = self.veh_pagina * self.veh_page_size
        rows = modelo.listar_vehiculos_paginados(
            limit=self.veh_page_size, offset=offset
        )

        # Inserta sólo los registros de esta página
        for placa, motor, marca, fe, fs, ced, tel in rows:
            self.tree_vehiculos.insert(
                "", "end", values=(placa, motor, marca, fe, fs, ced, tel)
            )

        # Actualiza etiqueta de estado
        total = modelo.contar_vehiculos()
        desde = offset + 1 if total > 0 else 0
        hasta = min(offset + self.veh_page_size, total)
        self.veh_label.config(text=f"{desde}-{hasta} de {total}")

    def configurar_paginacion_vehiculos(self, parent):
        # parent es el frame 'left' de la pestaña Vehículos
        # Inicializa variables
        self.veh_pagina = 0
        self.veh_page_size = 30

        # Etiqueta de rango
        self.veh_label = ttk.Label(parent, text="")
        self.veh_label.grid(row=13, column=0, pady=(0, 10))

        # Botones de navegación
        nav = ttk.Frame(parent)
        nav.grid(row=14, column=0)
        ttk.Button(nav, text="◀", command=self._veh_anterior).pack(side="left")
        ttk.Button(nav, text="▶", command=self._veh_siguiente).pack(side="left")

    def _veh_anterior(self):
        if self.veh_pagina > 0:
            self.veh_pagina -= 1
            self.cargar_vehiculos()

    def _veh_siguiente(self):
        total = modelo.contar_vehiculos()
        if (self.veh_pagina + 1) * self.veh_page_size < total:
            self.veh_pagina += 1
            self.cargar_vehiculos()

    def consultar_vehiculos_usuario(self):
        texto = self.consulta_combo.get()
        if not texto:
            messagebox.showwarning("Advertencia", "Seleccione un propietario")
            return
        ced = texto.split(" - ")[0].strip()
        if ced not in self.map_cedula_a_id:
            messagebox.showwarning("Advertencia", "Propietario no válido")
            return
        usuario_id = self.map_cedula_a_id[ced]
        vs = modelo.listar_vehiculos_por_usuario(usuario_id)
        for i in self.tree_resultado.get_children():
            self.tree_resultado.delete(i)
        for placa, motor, marca, fe, fs in vs:
            self.tree_resultado.insert("", "end", values=(placa, motor, marca))


def main():
    root = tk.Tk()
    app = VistaPrincipal(root)
    root.mainloop()


if __name__ == "__main__":
    main()
