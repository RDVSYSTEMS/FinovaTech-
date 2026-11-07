"""=============================================================
FinovaTech v10 - Modelo de usuarios (registro y login)
==============================================================
Lógica de REGISTRO y LOGIN contra MySQL (tabla "usuario").

Las contraseñas NUNCA se guardan en texto plano: se cifran con
werkzeug.security (generate_password_hash / check_password_hash).
=============================================================="""

import logging

import pymysql

from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_connection

logger = logging.getLogger(__name__)


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
    """Crea la cuenta y, si el rol es estudiante, su perfil financiero.

    RETORNA:
        (True, "Cuenta creada correctamente") o (False, mensaje_error).
    """
    if usuario_existe(email, username):
        return False, "Ya existe una cuenta con ese correo o nombre de usuario"

    # Solo se persiste el hash; la contraseña original nunca llega a MySQL.
    password_hash = generate_password_hash(password)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO usuario (nombre, email, username, password, rol) "
                "VALUES (%s, %s, %s, %s, %s)",
                (nombre, email, username, password_hash, rol),
            )
            usuario_id = cur.lastrowid
            # Solo el rol estudiante tiene perfil financiero; el padre supervisa
            # cuentas ajenas y no debe aparecer como estudiante.
            if rol == "estudiante":
                cur.execute(
                    "INSERT INTO estudiante (grado, institucion, saldo_actual, usuario_id) "
                    "VALUES (%s, %s, %s, %s)",
                    ("Sin definir", "Sin definir", 0.00, usuario_id),
                )
        conn.commit()
        return True, "Cuenta creada correctamente"
    except pymysql.MySQLError:
        conn.rollback()
        logger.exception("No se pudo registrar el usuario %s", email)
        return False, "No fue posible crear la cuenta en este momento"
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


def get_usuario_por_id(usuario_id: int):
    """Devuelve los datos públicos de la cuenta o None si no existe."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nombre, email, username, rol, fecha_registro "
                "FROM usuario WHERE id=%s",
                (usuario_id,),
            )
            return cur.fetchone()
    finally:
        conn.close()


def actualizar_datos_usuario(usuario_id: int, nombre: str, username: str):
    """Actualiza nombre y nombre de usuario, validando longitud y duplicados."""
    nombre = (nombre or "").strip()
    username = (username or "").strip()

    if not nombre or not username:
        return False, "Completa el nombre y el nombre de usuario"
    if len(nombre) > 100:
        return False, "El nombre no puede superar 100 caracteres"
    if len(username) < 4:
        return False, "El nombre de usuario debe tener mínimo 4 caracteres"
    if len(username) > 50:
        return False, "El nombre de usuario no puede superar 50 caracteres"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM usuario WHERE username=%s AND id<>%s",
                (username, usuario_id),
            )
            if cur.fetchone():
                return False, "Ese nombre de usuario ya está en uso"

            cur.execute("SELECT id FROM usuario WHERE id=%s", (usuario_id,))
            if not cur.fetchone():
                return False, "Usuario no encontrado"

            cur.execute(
                "UPDATE usuario SET nombre=%s, username=%s WHERE id=%s",
                (nombre, username, usuario_id),
            )
        conn.commit()
        return True, "Datos actualizados correctamente"
    except pymysql.MySQLError:
        conn.rollback()
        logger.exception("No se pudo actualizar el perfil del usuario %s", usuario_id)
        return False, "No fue posible actualizar los datos en este momento"
    finally:
        conn.close()


def cambiar_password_usuario(
    usuario_id: int, password_actual: str, password_nueva: str, confirmar: str
):
    """Cambia la contraseña verificando primero la actual y su confirmación."""
    if not password_actual or not password_nueva or not confirmar:
        return False, "Completa los tres campos de contraseña"
    if len(password_nueva) < 8:
        return False, "La nueva contraseña debe tener mínimo 8 caracteres"
    if password_nueva != confirmar:
        return False, "La nueva contraseña y su confirmación no coinciden"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password FROM usuario WHERE id=%s",
                (usuario_id,),
            )
            fila = cur.fetchone()
            if not fila:
                return False, "Usuario no encontrado"
            if not check_password_hash(fila["password"], password_actual):
                return False, "La contraseña actual es incorrecta"

            cur.execute(
                "UPDATE usuario SET password=%s WHERE id=%s",
                (generate_password_hash(password_nueva), usuario_id),
            )
        conn.commit()
        return True, "Contraseña actualizada correctamente"
    except pymysql.MySQLError:
        conn.rollback()
        logger.exception("No se pudo cambiar la contraseña del usuario %s", usuario_id)
        return False, "No fue posible cambiar la contraseña en este momento"
    finally:
        conn.close()