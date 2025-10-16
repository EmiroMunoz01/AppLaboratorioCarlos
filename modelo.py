import mysql.connector
from datetime import date
DB_CONFIG = {
    "host": "localhost",
    "database": "laboratorio_carlos",
    "user": "root",
    "password": "root",
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def initialize_db():
    sql_usuario = """
    CREATE TABLE IF NOT EXISTS usuario (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cedula VARCHAR(20) UNIQUE NOT NULL,
        nombre VARCHAR(50),
        apellido VARCHAR(50),
        telefono VARCHAR(25),
        direccion VARCHAR(120)
    );
    """
    sql_vehiculo = """
    CREATE TABLE IF NOT EXISTS vehiculo (
        placa VARCHAR(10) PRIMARY KEY,
        motor VARCHAR(50),
        marca VARCHAR(50),
        fecha_entrada DATE NOT NULL,
        fecha_salida DATE NULL,
        usuario_id INT,
        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
          ON DELETE CASCADE ON UPDATE CASCADE
    );
    """
    sql_cotizacion = """
    CREATE TABLE IF NOT EXISTS cotizacion (
        id INT AUTO_INCREMENT PRIMARY KEY,
        placa VARCHAR(10) NOT NULL,
        fecha DATE NOT NULL,
        total BIGINT NOT NULL,
        FOREIGN KEY (placa) REFERENCES vehiculo(placa)
          ON DELETE CASCADE ON UPDATE CASCADE
    );
    """
    sql_cotizacion_item = """
    CREATE TABLE IF NOT EXISTS cotizacion_item (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cotizacion_id INT NOT NULL,
        articulo VARCHAR(50),
        descripcion VARCHAR(200) NOT NULL,
        cantidad BIGINT NOT NULL,
        precio_unit BIGINT NOT NULL,
        total BIGINT NOT NULL,
        FOREIGN KEY (cotizacion_id) REFERENCES cotizacion(id)
          ON DELETE CASCADE
    );
    """ 
    sql_acta = """
    CREATE TABLE IF NOT EXISTS acta_garantia (
        id INT AUTO_INCREMENT PRIMARY KEY,
        placa VARCHAR(10) NOT NULL,
        fecha_elaboracion DATE NOT NULL,
        ruta_docx VARCHAR(255) NOT NULL,
        ruta_pdf  VARCHAR(255),
        observaciones VARCHAR(255),
        creado_por VARCHAR(60),
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (placa) REFERENCES vehiculo(placa)
          ON DELETE CASCADE ON UPDATE CASCADE
    );
    """
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(sql_usuario)
            cur.execute(sql_vehiculo)
            cur.execute(sql_cotizacion)
            cur.execute(sql_cotizacion_item)
            cur.execute(sql_acta)
        con.commit()
    finally:
        con.close()

# USUARIOS
def listar_usuarios():
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT id, cedula, nombre, apellido, telefono, direccion FROM usuario ORDER BY nombre")
            return cur.fetchall()
    finally:
        con.close()

def guardar_usuario(cedula,nombre,apellido,telefono,direccion=None):
    sql = """
    INSERT INTO usuario(cedula,nombre,apellido,telefono,direccion)
    VALUES(%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE nombre=VALUES(nombre),apellido=VALUES(apellido),
        telefono=VALUES(telefono),direccion=VALUES(direccion);
    """
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(sql,(cedula,nombre,apellido,telefono,direccion))
        con.commit()
    finally:
        con.close()

def actualizar_usuario(user_id,cedula,nombre,apellido,telefono,direccion=None):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                "UPDATE usuario SET cedula=%s,nombre=%s,apellido=%s,telefono=%s,direccion=%s WHERE id=%s",
                (cedula,nombre,apellido,telefono,direccion,user_id)
            )
            ok = cur.rowcount>0
        con.commit()
        return ok
    finally:
        con.close()

def eliminar_usuario(user_id):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM usuario WHERE id=%s",(user_id,))
            ok=cur.rowcount>0
        con.commit()
        return ok
    finally:
        con.close()

# VEHÍCULOS
def listar_vehiculos():
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("""
                SELECT v.placa,v.motor,v.marca,
                       DATE_FORMAT(v.fecha_entrada,'%Y-%m-%d'),
                       DATE_FORMAT(v.fecha_salida,'%Y-%m-%d'),
                       u.cedula,u.telefono
                  FROM vehiculo v
             LEFT JOIN usuario u ON u.id=v.usuario_id
              ORDER BY v.placa
            """)
            return cur.fetchall()
    finally:
        con.close()

def guardar_vehiculo(placa, motor, marca, fecha_entrada, fecha_salida, usuario_id):
    sql = """
    INSERT INTO vehiculo (placa, motor, marca, fecha_entrada, fecha_salida, usuario_id)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
      motor = VALUES(motor),
      marca = VALUES(marca),
      fecha_entrada = VALUES(fecha_entrada),
      fecha_salida = VALUES(fecha_salida),
      usuario_id = VALUES(usuario_id)
    """
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(sql, (placa, motor, marca, fecha_entrada, fecha_salida, usuario_id))
        con.commit()
    finally:
        con.close()


def actualizar_vehiculo(placa,motor,marca,fe,fs,uid):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                "UPDATE vehiculo SET motor=%s,marca=%s,fecha_entrada=%s,fecha_salida=%s,usuario_id=%s WHERE placa=%s",
                (motor,marca,fe,fs,uid,placa)
            )
            ok=cur.rowcount>0
        con.commit()
        return ok
    finally:
        con.close()

def eliminar_vehiculo(placa):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM vehiculo WHERE placa=%s",(placa,))
            ok=cur.rowcount>0
        con.commit()
        return ok
    finally:
        con.close()

def listar_vehiculos_por_usuario(uid):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("""
                SELECT placa,motor,marca,
                       DATE_FORMAT(fecha_entrada,'%Y-%m-%d'),
                       DATE_FORMAT(fecha_salida,'%Y-%m-%d')
                  FROM vehiculo
                 WHERE usuario_id=%s
              ORDER BY placa
            """,(uid,))
            return cur.fetchall()
    finally:
        con.close()

# COTIZACIONES
def guardar_cotizacion(placa, total, items):  # <-- Asegúrate que la firma es EXACTAMENTE esta.
    """
    Guarda una nueva cotización en la base de datos con la fecha actual.
    Recibe: placa, total e items.
    Devuelve: el ID de la cotización y la fecha generada.
    """
    fecha_actual = date.today().strftime('%Y-%m-%d')
    
    con = get_connection()
    try:
        with con.cursor() as cur:
            # Inserta la cotización principal
            cur.execute(
                "INSERT INTO cotizacion(placa, fecha, total) VALUES(%s, %s, %s)",
                (placa, fecha_actual, total)
            )
            cid = cur.lastrowid # Obtenemos el ID de la cotización recién creada
            
            # Inserta cada uno de los ítems
            for it in items:
                cur.execute(
                    "INSERT INTO cotizacion_item(cotizacion_id, articulo, descripcion, cantidad, precio_unit, total) "
                    "VALUES(%s, %s, %s, %s, %s, %s)",
                    (
                        cid,
                        it.get("articulo"),
                        it.get("descripcion"),
                        it.get("cantidad"),
                        it.get("precio_unit"),
                        it.get("total")
                    )
                )
        con.commit()
        # Devuelve ambos valores para que la vista los pueda usar
        return cid, fecha_actual
    finally:
        con.close()

def listar_cotizaciones_por_placa(placa):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT id,fecha,total FROM cotizacion WHERE placa=%s ORDER BY fecha DESC,id DESC",(placa,))
            return cur.fetchall()
    finally:
        con.close()

def eliminar_cotizacion(cid):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM cotizacion WHERE id=%s",(cid,))
            ok=cur.rowcount>0
        con.commit()
        return ok
    finally:
        con.close()

# ACTAS GARANTÍA con paginación
def crear_acta_garantia(
    placa,
    fecha_elaboracion,
    ruta_docx,
    ruta_pdf=None,
    obs=None,
    creado_por=None
):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                """
                INSERT INTO acta_garantia (
                    placa,
                    fecha_elaboracion,
                    ruta_docx,
                    ruta_pdf,
                    observaciones,
                    creado_por
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    placa,
                    fecha_elaboracion,
                    ruta_docx,
                    ruta_pdf,
                    obs,
                    creado_por
                )
            )
            aid = cur.lastrowid
        con.commit()
        return aid
    finally:
        con.close()


def contar_actas_por_placa(placa):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM acta_garantia WHERE placa=%s",(placa,))
            return cur.fetchone()[0]
    finally:
        con.close()

def listar_actas_por_placa(placa,limit=30,offset=0):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                "SELECT id,fecha_elaboracion,ruta_docx,ruta_pdf,observaciones "
                "FROM acta_garantia WHERE placa=%s "
                "ORDER BY fecha_elaboracion DESC,id DESC LIMIT %s OFFSET %s",
                (placa,limit,offset)
            )
            return cur.fetchall()
    finally:
        con.close()

def obtener_datos_acta(placa):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                "SELECT v.placa, DATE_FORMAT(v.fecha_entrada,'%Y-%m-%d'), DATE_FORMAT(v.fecha_salida,'%Y-%m-%d'), "
                "u.nombre,u.apellido,u.cedula,u.telefono,u.direccion,v.marca,v.motor "
                "FROM vehiculo v LEFT JOIN usuario u ON u.id=v.usuario_id WHERE v.placa=%s",
                (placa,)
            )
            return cur.fetchone()
    finally:
        con.close()

# Conteo y listado paginados para Vehículos
def contar_vehiculos():
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM vehiculo")
            return cur.fetchone()[0]
    finally:
        con.close()

def listar_vehiculos_paginados(limit=30, offset=0):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("""
                SELECT v.placa, v.motor, v.marca,
                       DATE_FORMAT(v.fecha_entrada,'%Y-%m-%d'),
                       DATE_FORMAT(v.fecha_salida,'%Y-%m-%d'),
                       u.cedula, u.telefono
                  FROM vehiculo v
             LEFT JOIN usuario u ON u.id=v.usuario_id
              ORDER BY v.placa
              LIMIT %s OFFSET %s
            """, (limit, offset))
            return cur.fetchall()
    finally:
        con.close()

# Conteo y listado paginados para Usuarios
def contar_usuarios():
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM usuario")
            return cur.fetchone()[0]
    finally:
        con.close()




# En modelo.py

def listar_items_por_cotizacion(cotizacion_id: int) -> list[dict]:
    """
    Devuelve una lista de dicts con los ítems asociados a la cotización.
    Cada dict tiene claves: articulo, descripcion, cantidad, precio_unit, total.
    """
    con = get_connection()
    try:
        with con.cursor(dictionary=True) as cur:
            cur.execute(
                """
                SELECT articulo, descripcion, cantidad, precio_unit AS precio_unit, total
                FROM cotizacion_item
                WHERE cotizacion_id = %s
                ORDER BY id
                """,
                (cotizacion_id,)
            )
            return cur.fetchall()
    finally:
        con.close()





def obtener_vehiculo_por_placa(placa: str) -> dict:
    """
    Devuelve un dict con los datos del vehículo y del usuario asociado.
    Lanza ValueError si no existe.
    """
    con = get_connection()
    try:
        with con.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT
                    v.placa,
                    v.motor,
                    v.marca,
                    DATE_FORMAT(v.fecha_entrada, '%Y-%m-%d')    AS fecha_entrada,
                    DATE_FORMAT(v.fecha_salida, '%Y-%m-%d')     AS fecha_salida,
                    u.id        AS usuario_id,
                    u.cedula,
                    u.nombre,
                    u.apellido,
                    u.telefono AS celular
                FROM vehiculo v
                JOIN usuario u ON v.usuario_id = u.id
                WHERE v.placa = %s
                """,
                (placa,)
            )
            fila = cursor.fetchone()
    finally:
        con.close()

    if not fila:
        raise ValueError(f"No existe vehículo con placa {placa}")

    return fila



def listar_usuarios_paginados(limit=30, offset=0):
    con = get_connection()
    try:
        with con.cursor() as cur:
            cur.execute("""
                SELECT id, cedula, nombre, apellido, telefono, direccion
                  FROM usuario
                 ORDER BY nombre
                 LIMIT %s OFFSET %s
            """, (limit, offset))
            return cur.fetchall()
    finally:
        con.close()
