import mysql.connector

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
        cedula INT UNIQUE NOT NULL,
        nombre VARCHAR(50),
        apellido VARCHAR(50),
        telefono VARCHAR(25)
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
        FOREIGN KEY (usuario_id)
          REFERENCES usuario(id)
          ON DELETE CASCADE
          ON UPDATE CASCADE
    );
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql_usuario)
            cur.execute(sql_vehiculo)
        conn.commit()
    finally:
        conn.close()


# ------------------- USUARIOS -------------------


def buscar_usuario(cedula):
    sql = "SELECT id, cedula, nombre, apellido, telefono FROM usuario WHERE cedula=%s"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (cedula,))
            return cur.fetchone()
    finally:
        conn.close()


def listar_usuarios():
    sql = "SELECT id, cedula, nombre, apellido, telefono FROM usuario ORDER BY nombre"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


def guardar_usuario(cedula, nombre, apellido, telefono):
    sql = """
    INSERT INTO usuario (cedula,nombre,apellido,telefono)
    VALUES (%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      nombre=VALUES(nombre),
      apellido=VALUES(apellido),
      telefono=VALUES(telefono);
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (cedula, nombre, apellido, telefono))
        conn.commit()
    finally:
        conn.close()


def actualizar_usuario(user_id, nueva_cedula, nombre, apellido, telefono):
    sql = """
    UPDATE usuario
       SET cedula=%s, nombre=%s, apellido=%s, telefono=%s
     WHERE id=%s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (nueva_cedula, nombre, apellido, telefono, user_id))
            actualizado = cur.rowcount > 0
        conn.commit()
        return actualizado
    finally:
        conn.close()


def eliminar_usuario(user_id):
    sql = "DELETE FROM usuario WHERE id=%s"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            eliminado = cur.rowcount > 0
        conn.commit()
        return eliminado
    finally:
        conn.close()


# ------------------- VEHÍCULOS -------------------


def listar_vehiculos():
    sql = """
    SELECT v.placa, v.motor, v.marca,
           DATE_FORMAT(v.fecha_entrada,'%Y-%m-%d'),
           DATE_FORMAT(v.fecha_salida,'%Y-%m-%d'),
           u.cedula, u.telefono
      FROM vehiculo v
 LEFT JOIN usuario u ON v.usuario_id = u.id
  ORDER BY v.placa
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


def guardar_vehiculo(placa, motor, marca, fecha_entrada, fecha_salida, usuario_id):
    sql = """
    INSERT INTO vehiculo (placa,motor,marca,fecha_entrada,fecha_salida,usuario_id)
    VALUES (%s,%s,%s,%s,%s,%s);
    """
    fs = fecha_salida if fecha_salida else None
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (placa, motor, marca, fecha_entrada, fs, usuario_id))
        conn.commit()
    finally:
        conn.close()


def actualizar_vehiculo(placa, motor, marca, fecha_entrada, fecha_salida, usuario_id):
    sql = """
    UPDATE vehiculo
       SET motor=%s, marca=%s, fecha_entrada=%s, fecha_salida=%s, usuario_id=%s
     WHERE placa=%s
    """
    fs = fecha_salida if fecha_salida else None
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (motor, marca, fecha_entrada, fs, usuario_id, placa))
            actualizado = cur.rowcount > 0
        conn.commit()
        return actualizado
    finally:
        conn.close()


def eliminar_vehiculo(placa):
    sql = "DELETE FROM vehiculo WHERE placa=%s"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (placa,))
            eliminado = cur.rowcount > 0
        conn.commit()
        return eliminado
    finally:
        conn.close()


def listar_vehiculos_por_usuario(usuario_id):
    sql = """
    SELECT placa, motor, marca,
           DATE_FORMAT(fecha_entrada,'%Y-%m-%d'),
           DATE_FORMAT(fecha_salida,'%Y-%m-%d')
      FROM vehiculo
     WHERE usuario_id=%s
  ORDER BY placa
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (usuario_id,))
            return cur.fetchall()
    finally:
        conn.close()
