"""=============================================================
FinovaTech v10 - Recuperación de contraseña
==============================================================
Genera tokens de un solo uso y actualiza el hash de la cuenta.
En la base solo se guarda el SHA-256 del token.
=============================================================="""

import hashlib
import logging
import secrets

from datetime import datetime, timedelta

import pymysql

from werkzeug.security import generate_password_hash

from app.config import Config
from app.db import get_connection

logger = logging.getLogger(__name__)


def _hash_token(token: str) -> str:
    """Devuelve el SHA-256 hexadecimal del token para almacenarlo en la BD."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def buscar_usuario_por_email(email: str):
    """Cuenta mínima necesaria para enviar el enlace (o None)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nombre, email FROM usuario WHERE email=%s",
                ((email or "").strip().lower(),),
            )
            return cur.fetchone()
    finally:
        conn.close()


def crear_token_recuperacion(usuario_id: int, ip: str = ""):
    """Crea un token nuevo e invalida los anteriores del mismo usuario."""
    token = secrets.token_urlsafe(32)
    expira = datetime.now() + timedelta(minutes=Config.PASSWORD_RESET_MINUTES)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE recuperacion_password SET usado_en=NOW() "
                "WHERE usuario_id=%s AND usado_en IS NULL",
                (usuario_id,),
            )
            cur.execute(
                "INSERT INTO recuperacion_password "
                "(usuario_id, token_hash, expira_en, ip_solicitud) "
                "VALUES (%s, %s, %s, %s)",
                (usuario_id, _hash_token(token), expira, (ip or "")[:45]),
            )
        conn.commit()
        return token
    except pymysql.MySQLError:
        conn.rollback()
        logger.exception("No se pudo crear el token de recuperación")
        return None
    finally:
        conn.close()


def validar_token(token: str):
    """Devuelve id, nombre y email del usuario si el token sigue vigente."""
    if not token:
        return None
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT u.id, u.nombre, u.email "
                "FROM recuperacion_password r "
                "JOIN usuario u ON u.id=r.usuario_id "
                "WHERE r.token_hash=%s AND r.usado_en IS NULL AND r.expira_en > NOW()",
                (_hash_token(token),),
            )
            return cur.fetchone()
    finally:
        conn.close()


def restablecer_password(token: str, nueva: str, confirmar: str) -> tuple:
    """Valida el token y cambia la contraseña una sola vez."""
    if not nueva or not confirmar:
        return False, "Completa los dos campos de contraseña"
    if len(nueva) < 8:
        return False, "La nueva contraseña debe tener mínimo 8 caracteres"
    if nueva != confirmar:
        return False, "La nueva contraseña y su confirmación no coinciden"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT r.id AS token_id, r.usuario_id "
                "FROM recuperacion_password r "
                "WHERE r.token_hash=%s AND r.usado_en IS NULL AND r.expira_en > NOW() "
                "FOR UPDATE",
                (_hash_token(token),),
            )
            fila = cur.fetchone()
            if not fila:
                conn.rollback()
                return False, "El enlace no es válido o ya expiró"

            cur.execute(
                "UPDATE usuario SET password=%s WHERE id=%s",
                (generate_password_hash(nueva), fila["usuario_id"]),
            )
            cur.execute(
                "UPDATE recuperacion_password SET usado_en=NOW() WHERE id=%s",
                (fila["token_id"],),
            )
        conn.commit()
        return True, "Contraseña actualizada correctamente. Ya puedes iniciar sesión."
    except pymysql.MySQLError:
        conn.rollback()
        logger.exception("No se pudo restablecer la contraseña")
        return False, "No fue posible actualizar la contraseña"
    finally:
        conn.close()
