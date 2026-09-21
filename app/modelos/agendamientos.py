"""Operaciones de agendamiento de sesiones."""

from datetime import date, datetime

import pymysql

from app.db import get_connection

CATEGORIAS_VALIDAS = {"reserva", "consultoria", "taller"}
ESTADOS_VALIDOS = {"pendiente", "confirmado", "cancelado", "completado"}


def crear_agendamiento(usuario_id: int, fecha: str, hora: str, categoria: str,
                       estado: str, comentarios: str):
    """Guarda una sesión y devuelve (éxito, mensaje)."""
    try:
        fecha_valor = datetime.strptime(fecha, "%Y-%m-%d").date()
        datetime.strptime(hora, "%H:%M")
    except (TypeError, ValueError):
        return False, "La fecha o la hora no tienen un formato válido"

    if fecha_valor < date.today():
        return False, "La fecha no puede ser anterior a hoy"
    if categoria not in CATEGORIAS_VALIDAS:
        return False, "La categoría seleccionada no es válida"
    if estado not in ESTADOS_VALIDOS:
        return False, "El estado seleccionado no es válido"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO agendamiento "
                "(usuario_id, fecha, hora, categoria, estado, comentarios) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (usuario_id, fecha_valor, hora, categoria, estado, comentarios[:1000]),
            )
        conn.commit()
    except pymysql.MySQLError:
        conn.rollback()
        return False, "No fue posible guardar la sesión"
    finally:
        conn.close()

    return True, "Sesión agendada correctamente"
