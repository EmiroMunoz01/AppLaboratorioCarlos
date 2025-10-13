import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import modelo


class VistaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("LABORATORIO SUR DIESEL PITALITO")
        self.root.geometry("1000x700")

        # estado
        self.placa_original = None
        self.usuario_id_sel = None  # id del usuario seleccionado en el Treeview

        modelo.initialize_db()
        self.crear_interfaz()
        self.cargar_datos_iniciales()

    def cargar_datos_iniciales(self):
        self.cargar_usuarios()
        self.cargar_vehiculos()
        self.cargar_propietarios()

    def crear_interfaz(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.frame_usuarios = ttk.Frame(self.notebook)
        self.frame_vehiculos = ttk.Frame(self.notebook)
        self.frame_consultas = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_usuarios, text="👤 Usuarios")
        self.notebook.add(self.frame_vehiculos, text="🚗 Vehículos")
        self.notebook.add(self.frame_consultas, text="📊 Consultas")

        self.crear_pestaña_usuarios()
        self.crear_pestaña_vehiculos()
        self.crear_pestaña_consultas()

    # ---------------- Usuarios ----------------
    def crear_pestaña_usuarios(self):
        main = ttk.Frame(self.frame_usuarios)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.LabelFrame(main, text="Datos del Usuario", padding=15)
        left.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(left, text="Cédula:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.cedula_entry = ttk.Entry(left)
        self.cedula_entry.grid(row=1, column=0, pady=(0, 10))

        ttk.Label(left, text="Nombre:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.nombre_entry = ttk.Entry(left)
        self.nombre_entry.grid(row=3, column=0, pady=(0, 10))

        ttk.Label(left, text="Apellido:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=5)
        self.apellido_entry = ttk.Entry(left)
        self.apellido_entry.grid(row=5, column=0, pady=(0, 10))

        ttk.Label(left, text="Teléfono:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky="w", pady=5)
        self.telefono_entry = ttk.Entry(left)
        self.telefono_entry.grid(row=7, column=0, pady=(0, 15))

        btns = ttk.Frame(left)
        btns.grid(row=8, column=0, pady=10)
        ttk.Button(btns, text="💾 Guardar", command=self.guardar_usuario).pack(pady=2)
        ttk.Button(btns, text="✏️ Actualizar", command=self.actualizar_usuario).pack(pady=2)
        ttk.Button(btns, text="🗑️ Eliminar", command=self.eliminar_usuario).pack(pady=2)
        ttk.Button(btns, text="🆕 Nuevo", command=self.limpiar_usuario).pack(pady=2)

        right = ttk.LabelFrame(main, text="Lista de Usuarios", padding=10)
        right.pack(side="right", fill="both", expand=True)

        sf = ttk.Frame(right)
        sf.pack(fill="x", pady=(0, 10))
        ttk.Label(sf, text="Buscar:").pack(side="left")
        self.buscar_usuario_entry = ttk.Entry(sf, width=20)
        self.buscar_usuario_entry.pack(side="left", padx=5)
        ttk.Button(sf, text="🔍", command=self.buscar_usuarios).pack(side="left")
        ttk.Button(sf, text="📋 Todos", command=self.cargar_usuarios).pack(side="left", padx=5)

        cols_usr = ("Cédula", "Nombre", "Apellido", "Teléfono")
        self.tree_usuarios = ttk.Treeview(right, columns=cols_usr, show="headings", height=20)
        for c in cols_usr:
            self.tree_usuarios.heading(c, text=c)
            self.tree_usuarios.column(c, width=120)
        sb = ttk.Scrollbar(right, orient="vertical", command=self.tree_usuarios.yview)
        self.tree_usuarios.configure(yscrollcommand=sb.set)
        self.tree_usuarios.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_usuarios.bind("<<TreeviewSelect>>", self.seleccionar_usuario)

    # ---------------- Vehículos ----------------
    def crear_pestaña_vehiculos(self):
        main = ttk.Frame(self.frame_vehiculos)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.LabelFrame(main, text="Datos del Vehículo", padding=15)
        left.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(left, text="Placa:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.placa_entry = ttk.Entry(left)
        self.placa_entry.grid(row=1, column=0, pady=(0, 10))

        ttk.Label(left, text="Motor:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.motor_entry = ttk.Entry(left)
        self.motor_entry.grid(row=3, column=0, pady=(0, 10))

        ttk.Label(left, text="Marca:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=5)
        self.marca_entry = ttk.Entry(left)
        self.marca_entry.grid(row=5, column=0, pady=(0, 10))

        ttk.Label(left, text="Fecha Entrada:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky="w", pady=5)
        self.fecha_entry = DateEntry(left, date_pattern="yyyy-MM-dd")
        self.fecha_entry.grid(row=7, column=0, pady=(0, 10))

        ttk.Label(left, text="Fecha Salida:", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky="w", pady=5)
        self.fecha_salida_entry = DateEntry(left, date_pattern="yyyy-MM-dd")
        self.fecha_salida_entry.grid(row=9, column=0, pady=(0, 15))
        self.fecha_salida_entry.delete(0, tk.END)  # permitir vacío

        ttk.Label(left, text="Propietario:", font=("Arial", 10, "bold")).grid(row=10, column=0, sticky="w", pady=5)
        self.propietario_combo = ttk.Combobox(left, state="readonly")
        self.propietario_combo.grid(row=11, column=0, pady=(0, 15))

        btns = ttk.Frame(left)
        btns.grid(row=12, column=0, pady=10)
        ttk.Button(btns, text="💾 Guardar", command=self.guardar_vehiculo).pack(pady=2)
        ttk.Button(btns, text="✏️ Actualizar", command=self.actualizar_vehiculo).pack(pady=2)
        ttk.Button(btns, text="🗑️ Eliminar", command=self.eliminar_vehiculo).pack(pady=2)
        ttk.Button(btns, text="🆕 Nuevo", command=self.limpiar_vehiculo).pack(pady=2)
        ttk.Button(btns, text="🔄 Recargar", command=self.cargar_propietarios).pack(pady=2)

        right = ttk.LabelFrame(main, text="Lista de Vehículos", padding=10)
        right.pack(side="right", fill="both", expand=True)

        cols_veh = ("Placa", "Motor", "Marca", "Fecha Entrada", "Fecha Salida", "Propietario", "Teléfono")
        self.tree_vehiculos = ttk.Treeview(right, columns=cols_veh, show="headings", height=25)
        for c in cols_veh:
            self.tree_vehiculos.heading(c, text=c)
            self.tree_vehiculos.column(c, width=120)
        sb = ttk.Scrollbar(right, orient="vertical", command=self.tree_vehiculos.yview)
        self.tree_vehiculos.configure(yscrollcommand=sb.set)
        self.tree_vehiculos.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_vehiculos.bind("<<TreeviewSelect>>", self.seleccionar_vehiculo)

    def crear_pestaña_consultas(self):
        main = ttk.Frame(self.frame_consultas)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(main, text="Vehículos por Propietario", font=("Arial", 12, "bold")).pack(anchor="w")
        self.consulta_combo = ttk.Combobox(main, state="readonly")
        self.consulta_combo.pack(anchor="w", pady=5)
        ttk.Button(main, text="🔍 Consultar", command=self.consultar_vehiculos_usuario).pack(anchor="w", pady=5)
        self.tree_resultado = ttk.Treeview(main, columns=("Placa", "Motor", "Marca"), show="headings", height=10)
        for c in ("Placa", "Motor", "Marca"):
            self.tree_resultado.heading(c, text=c)
            self.tree_resultado.column(c, width=120)
        sb2 = ttk.Scrollbar(main, orient="vertical", command=self.tree_resultado.yview)
        self.tree_resultado.configure(yscrollcommand=sb2.set)
        self.tree_resultado.pack(fill="both", expand=True)
        sb2.pack(side="right", fill="y")

    # --------- Eventos/CRUD Usuarios ---------
    def seleccionar_usuario(self, event):
        sel = self.tree_usuarios.selection()
        if not sel:
            return
        # guardar id desde el iid del item
        self.usuario_id_sel = int(sel[0])
        ced, nom, ape, tel = self.tree_usuarios.item(sel[0])["values"]

        self.cedula_entry.delete(0, tk.END); self.cedula_entry.insert(0, ced)
        self.nombre_entry.delete(0, tk.END); self.nombre_entry.insert(0, nom)
        self.apellido_entry.delete(0, tk.END); self.apellido_entry.insert(0, ape)
        self.telefono_entry.delete(0, tk.END); self.telefono_entry.insert(0, tel)

    # --------- Eventos/CRUD Vehículos ---------
    def seleccionar_vehiculo(self, event):
        sel = self.tree_vehiculos.selection()
        if not sel:
            return
        placa, motor, marca, fe, fs, ced, tel = self.tree_vehiculos.item(sel[0])["values"]

        # guarda placa original y bloquea edición de la placa
        self.placa_original = placa
        self.placa_entry.config(state="normal")
        self.placa_entry.delete(0, tk.END)
        self.placa_entry.insert(0, placa)
        self.placa_entry.config(state="disabled")

        self.motor_entry.delete(0, tk.END); self.motor_entry.insert(0, motor)
        self.marca_entry.delete(0, tk.END); self.marca_entry.insert(0, marca)
        self.fecha_entry.set_date(fe)
        if fs and fs != "None":
            self.fecha_salida_entry.set_date(fs)
        else:
            self.fecha_salida_entry.delete(0, tk.END)
        self.propietario_combo.set(f"{ced} - {tel}")

    # ----------------- Usuarios -----------------
    def guardar_usuario(self):
        try:
            ced = int(self.cedula_entry.get().strip())
            nom = self.nombre_entry.get().strip()
            ape = self.apellido_entry.get().strip()
            tel = self.telefono_entry.get().strip()
            modelo.guardar_usuario(ced, nom, ape, tel)
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
            ok = modelo.actualizar_usuario(self.usuario_id_sel, nueva_ced, nom, ape, tel)
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

    def buscar_usuarios(self):
        # pendiente: implementar búsqueda por nombre/cedula si se requiere
        pass

    def cargar_usuarios(self):
        for i in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(i)
        for usr in modelo.listar_usuarios():
            # usr = (id, cedula, nombre, apellido, telefono)
            self.tree_usuarios.insert("", "end", iid=str(usr[0]), values=usr[1:])

    # ----------------- Vehículos -----------------
    def guardar_vehiculo(self):
        try:
            placa = self.placa_entry.get().strip().upper()
            motor = self.motor_entry.get().strip()
            marca = self.marca_entry.get().strip()
            fe = self.fecha_entry.get_date().strftime("%Y-%m-%d")
            fs_text = self.fecha_salida_entry.get().strip()
            fs = fs_text if fs_text else None
            uid = int(self.propietario_combo.get().split(" - ")[0])
            modelo.guardar_vehiculo(placa, motor, marca, fe, fs, uid)
            messagebox.showinfo("Éxito", "Vehículo guardado")
            self.cargar_vehiculos()
            self.placa_original = None
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_vehiculo(self):
        try:
            if not self.placa_original:
                messagebox.showwarning("Aviso", "Seleccione un vehículo de la lista para actualizar")
                return
            placa_nueva = self.placa_entry.get().strip().upper()  # queda igual, está bloqueada
            motor = self.motor_entry.get().strip()
            marca = self.marca_entry.get().strip()
            fe = self.fecha_entry.get_date().strftime("%Y-%m-%d")
            fs_text = self.fecha_salida_entry.get().strip()
            fs = fs_text if fs_text else None
            uid = int(self.propietario_combo.get().split(" - ")[0])

            ok = modelo.actualizar_vehiculo(self.placa_original, motor, marca, fe, fs, uid)
            if ok:
                messagebox.showinfo("Éxito", "Vehículo actualizado")
            else:
                messagebox.showwarning("Aviso", "No se encontró ese vehículo")
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
        vals = [f"{u[0]} - {u[2]} {u[3]}" for u in usuarios]
        self.propietario_combo["values"] = vals
        self.consulta_combo["values"] = vals

    def cargar_vehiculos(self):
        for i in self.tree_vehiculos.get_children():
            self.tree_vehiculos.delete(i)
        for placa, motor, marca, fe, fs, ced, tel in modelo.listar_vehiculos():
            self.tree_vehiculos.insert("", "end", values=(placa, motor, marca, fe, fs, ced, tel))

    def consultar_vehiculos_usuario(self):
        texto = self.consulta_combo.get()
        if not texto:
            messagebox.showwarning("Advertencia", "Seleccione un propietario")
            return
        ced = int(texto.split(" - ")[0])
        vs = modelo.listar_vehiculos_por_usuario(ced)
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
