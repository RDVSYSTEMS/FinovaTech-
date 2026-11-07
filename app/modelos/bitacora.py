"""=============================================================
FinovaTech v10 - Bitácora de accesos
==============================================================
Registra eventos de autenticación sin interrumpir el flujo
principal si la escritura falla.
=============================================================="""

import logging

import pymysql

from app.db import get_connection

logger = logging.getLogger(__name__)

EVENTOS = {
    "login_ok": "Inicio de sesión correcto",
    "login_fallido": "Intento fallido",
    "bloqueo": "Bloqueo por intentos",
    "logout": "Cierre de sesión",
    "recuperacion_solicitada": "Recuperación solicitada",
    "recuperacion_completada": "Contraseña restablecida",
}


def registrar_acceso(usuario_id, email: str, evento: str, ip: str, detalle: str = ""):
    """Inserta un evento; nunca lanza excepción hacia el login."""
    if evento not in EVENTOS:
        return
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO bitacora_acceso "
                    "(usuario_id, email, evento, ip, detalle) VALUES (%s, %s, %s, %s, %s)",
                    (usuario_id, (email or "")[:120], evento, (ip or "")[:45], (detalle or "")[:255]),
                )
            conn.commit()
        finally:
            conn.close()
    except pymysql.MySQLError:
        logger.exception("No se pudo registrar el evento de acceso %s", evento)


def get_accesos(limite: int = 100) -> list:
    """Últimos eventos de acceso, del más reciente al más antiguo."""
    limite = max(1, min(int(limite), 500))
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT usuario_id, email, evento, ip, detalle, creado_en "
                "FROM bitacora_acceso ORDER BY creado_en DESC, id DESC LIMIT %s",
                (limite,),
            )
            filas = list(cur.fetchall())
    finally:
        conn.close()

    for fila in filas:
        fila["evento_texto"] = EVENTOS.get(fila["evento"], fila["evento"])
    return filas
