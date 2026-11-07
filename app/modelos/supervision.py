"""=============================================================
FinovaTech v10 - Modelo de supervisión del rol padre
==============================================================
Gestiona el código de vinculación del estudiante y la relación
de solo lectura padre -> estudiante.
=============================================================="""

import logging
import secrets

import pymysql

from app.db import get_connection

logger = logging.getLogger(__name__)

ALFABETO_CODIGO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _codigo_nuevo() -> str:
    """Genera un código de 8 caracteres sin ambigüedades (0/O, 1/I)."""
    return "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(8))


def obtener_o_crear_codigo_vinculacion(usuario_id: int):
    """Devuelve el código del estudiante, creándolo la primera vez."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT codigo_vinculacion FROM estudiante WHERE usuario_id=%s",
                (usuario_id,),
            )
            fila = cur.fetchone()
            if not fila:
                return None
            if fila["codigo_vinculacion"]:
                return fila["codigo_vinculacion"]

            # Se reintenta si un código aleatorio choca con el UNIQUE.
            for _ in range(10):
                codigo = _codigo_nuevo()
                try:
                    cur.execute(
                        "UPDATE estudiante SET codigo_vinculacion=%s "
                        "WHERE usuario_id=%s AND codigo_vinculacion IS NULL",
                        (codigo, usuario_id),
                    )
                    conn.commit()
                    return codigo
                except pymysql.err.IntegrityError:
                    conn.rollback()
            return None
    finally:
        conn.close()


def vincular_por_codigo(padre_id: int, codigo: str) -> tuple:
    """Vincula una cuenta de estudiante al padre usando su código."""
    codigo = (codigo or "").strip().upper()
    if len(codigo) < 6 or len(codigo) > 12:
        return False, "Ingresa un código de vinculación válido"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT u.id, u.nombre, u.email "
                "FROM estudiante e JOIN usuario u ON u.id=e.usuario_id "
                "WHERE e.codigo_vinculacion=%s AND u.rol='estudiante'",
                (codigo,),
            )
            estudiante = cur.fetchone()
            if not estudiante:
                return False, "El código no corresponde a un estudiante válido"
            if estudiante["id"] == padre_id:
                return False, "No puedes vincularte a tu propia cuenta"

            cur.execute(
                "INSERT IGNORE INTO padre_estudiante "
                "(padre_id, estudiante_usuario_id) VALUES (%s, %s)",
                (padre_id, estudiante["id"]),
            )
            if cur.rowcount == 0:
                return False, "Ese estudiante ya está vinculado a tu cuenta"
        conn.commit()
    except pymysql.MySQLError:
        conn.rollback()
        logger.exception("No se pudo vincular padre %s con código", padre_id)
        return False, "No fue posible completar la vinculación"
    finally:
        conn.close()

    return True, f"Vinculaste a {estudiante['nombre']} correctamente"


def get_estudiantes_vinculados(padre_id: int) -> list:
    """Cuentas de estudiante vinculadas al padre actual."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT u.id, u.nombre, u.email, u.username "
                "FROM padre_estudiante pe "
                "JOIN usuario u ON u.id=pe.estudiante_usuario_id "
                "WHERE pe.padre_id=%s ORDER BY u.nombre",
                (padre_id,),
            )
            return list(cur.fetchall())
    finally:
        conn.close()


def desvincular_estudiante(padre_id: int, estudiante_usuario_id: int) -> tuple:
    """Elimina un vínculo solo si pertenece al padre actual."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM padre_estudiante "
                "WHERE padre_id=%s AND estudiante_usuario_id=%s",
                (padre_id, estudiante_usuario_id),
            )
            afectadas = cur.rowcount
        conn.commit()
    except pymysql.MySQLError:
        conn.rollback()
        logger.exception("No se pudo desvincular al estudiante %s", estudiante_usuario_id)
        return False, "No fue posible quitar el vínculo"
    finally:
        conn.close()

    if afectadas == 0:
        return False, "El vínculo no existe o no te pertenece"
    return True, "Vínculo eliminado correctamente"
