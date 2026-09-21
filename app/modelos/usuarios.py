"""=============================================================
FinovaTech v9 - Modelo de usuarios (registro y login)
==============================================================
Lógica de REGISTRO y LOGIN contra MySQL (tabla "usuario").

Las contraseñas NUNCA se guardan en texto plano: se cifran con
werkzeug.security (generate_password_hash / check_password_hash).
=============================================================="""

from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_connection


def usuario_existe(email: str, username: str) -> bool:
    """Comprueba duplicados antes de crear una cuenta."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM usuario WHERE email=%s OR username=%s",
                (email, username),
            )
            return cur.fetchone() is not None
    finally:
        conn.close()


def registrar_usuario(nombre: str, email: str, username: str, password: str, rol: str):
    """Crea la cuenta + su perfil de estudiante por defecto.

    RETORNA:
        (True, "Cuenta creada correctamente") o (False, mensaje_error).
    """
    if usuario_existe(email, username):
        return False, "Ya existe una cuenta con ese correo o nombre de usuario"

    # Solo se persiste el hash; la contraseña original nunca llega a MySQL.
    password_hash = generate_password_hash(password)

    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO usuario (nombre, email, username, password, rol) "
                "VALUES (%s, %s, %s, %s, %s)",
                (nombre, email, username, password_hash, rol),
            )
            usuario_id = cur.lastrowid
            cur.execute(
                "INSERT INTO estudiante (grado, institucion, saldo_actual, usuario_id) "
                "VALUES (%s, %s, %s, %s)",
                ("Sin definir", "Sin definir", 0.00, usuario_id),
            )
        conn.commit()
        return True, "Cuenta creada correctamente"
    except Exception as e:
        return False, f"Error al registrar: {e}"
    finally:
        conn.close()


def verificar_login(email: str, password: str):
    """Devuelve el usuario (dict) si las credenciales son correctas, si no None."""
    # La contraseña se verifica contra el hash recuperado, nunca en SQL plano.
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuario WHERE email=%s", (email,))
            user = cur.fetchone()
    finally:
        conn.close()

    if user and check_password_hash(user["password"], password):
        return user
    return None