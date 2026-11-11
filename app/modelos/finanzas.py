"""=============================================================
FinovaTech v10 - Modelo financiero (datos, registros, notificaciones)
==============================================================
Consulta la base de datos para el panel, la lista de movimientos
y las notificaciones de un usuario.

Tablas usadas (esquema finovatech): usuario, estudiante, ingreso,
gasto, presupuesto.

Formato de dinero: _fmt() convierte 440000 en "$440.000"
(estilo colombiano, con puntos de miles).
=============================================================="""

import logging

import csv
import io

import pymysql

from datetime import date, datetime as _dt_datetime, timedelta

from app.db import get_connection

logger = logging.getLogger(__name__)

MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

MESES_LARGOS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre",
                "Diciembre"]


def _fmt(valor) -> str:
    """Formatea un importe como pesos colombianos sin decimales."""
    return "$" + "{:,.0f}".format(float(valor)).replace(",", ".")


def _ultimos_meses(n: int = 6):
    """Lista de los últimos n meses (con el mes actual al final), como date(1)."""
    ahora = date.today()
    lista = []
    for i in range(n - 1, -1, -1):
        lineal = ahora.year * 12 + (ahora.month - 1) - i
        anio, mes0 = divmod(lineal, 12)
        lista.append(date(anio, mes0 + 1, 1))
    return lista


def _formatear_movimiento(fila: dict) -> dict:
    """Convierte una fila de UNION ALL (ingreso/gasto) en dict para la plantilla."""
    return {
        "tipo": fila["tipo"],
        "descripcion": fila["descripcion"],
        "monto_texto": _fmt(fila["monto"]),
        "fecha": fila["fecha"].strftime("%d/%m/%Y") if fila["fecha"] else "",
        "id": fila["id"],
    }


def get_estudiante_id(usuario_id: int):
    """Id del perfil de estudiante vinculado al usuario (o None)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM estudiante WHERE usuario_id=%s", (usuario_id,))
            row = cur.fetchone()
            return row["id"] if row else None
    finally:
        conn.close()


# --- Panel -------------------------------------------------------------------

def get_datos_panel(usuario_id: int) -> dict:
    """Todos los datos que necesita panel.html (totales, movimientos, categorías,
    presupuesto y evolución mensual)."""
    # Se devuelve una estructura completa incluso sin perfil o movimientos,
    # para que el template pueda renderizar estados vacíos sin condiciones extra.
    datos = {
        "total_ingresos": "$0",
        "total_gastos": "$0",
        "balance": "$0",
        "total_registros": 0,
        "movimientos": [],
        "hay_movimientos": False,
        "categorias": [],
        "hay_categorias": False,
        "presupuesto": None,
        "evolucion": [],
        "hay_evolucion": False,
        "categorias_datos": [],
    }

    estudiante_id = get_estudiante_id(usuario_id)
    if estudiante_id is None:
        return datos

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(SUM(monto),0) AS s FROM ingreso WHERE estudiante_id=%s",
                (estudiante_id,),
            )
            total_ingresos = float(cur.fetchone()["s"])

            cur.execute(
                "SELECT COALESCE(SUM(monto),0) AS s FROM gasto WHERE estudiante_id=%s",
                (estudiante_id,),
            )
            total_gastos = float(cur.fetchone()["s"])

            cur.execute(
                "SELECT (SELECT COUNT(*) FROM ingreso WHERE estudiante_id=%s) "
                "+ (SELECT COUNT(*) FROM gasto WHERE estudiante_id=%s) AS t",
                (estudiante_id, estudiante_id),
            )
            total_registros = int(cur.fetchone()["t"])

            balance = total_ingresos - total_gastos

            cur.execute(
                "SELECT 'Ingreso' AS tipo, descripcion, monto, fecha FROM ingreso "
                "WHERE estudiante_id=%s "
                "UNION ALL "
                "SELECT 'Gasto' AS tipo, descripcion, monto, fecha FROM gasto "
                "WHERE estudiante_id=%s "
                "ORDER BY fecha DESC LIMIT 6",
                (estudiante_id, estudiante_id),
            )
            movimientos = cur.fetchall()

            cur.execute(
                "SELECT categoria, SUM(monto) AS total FROM gasto "
                "WHERE estudiante_id=%s "
                "GROUP BY categoria ORDER BY total DESC",
                (estudiante_id,),
            )
            por_categoria = cur.fetchall()

            cur.execute(
                "SELECT monto_limite, periodo, fecha_inicio, fecha_fin "
                "FROM presupuesto WHERE estudiante_id=%s "
                "ORDER BY fecha_inicio DESC LIMIT 1",
                (estudiante_id,),
            )
            presupuesto_row = cur.fetchone()

            cur.execute(
                "SELECT DATE_FORMAT(fecha, '%%Y-%%m') AS mes, SUM(monto) AS s "
                "FROM ingreso WHERE estudiante_id=%s GROUP BY mes",
                (estudiante_id,),
            )
            ingresos_por_mes = {r["mes"]: float(r["s"]) for r in cur.fetchall()}

            cur.execute(
                "SELECT DATE_FORMAT(fecha, '%%Y-%%m') AS mes, SUM(monto) AS s "
                "FROM gasto WHERE estudiante_id=%s GROUP BY mes",
                (estudiante_id,),
            )
            gastos_por_mes = {r["mes"]: float(r["s"]) for r in cur.fetchall()}
    finally:
        conn.close()

    datos["total_ingresos"] = _fmt(total_ingresos)
    datos["total_gastos"] = _fmt(total_gastos)
    datos["balance"] = _fmt(balance)
    datos["total_registros"] = total_registros
    datos["hay_movimientos"] = bool(movimientos)

    for m in movimientos:
        datos["movimientos"].append({
            "tipo": m["tipo"],
            "descripcion": m["descripcion"],
            "monto": _fmt(m["monto"]),
            "fecha": m["fecha"].strftime("%d/%m/%Y") if m["fecha"] else "",
        })

    datos["hay_categorias"] = bool(por_categoria)
    if por_categoria:
        datos["categorias"] = [
            {
                "categoria": c["categoria"],
                "total": _fmt(c["total"]),
                "porcentaje": int(round(float(c["total"]) / total_gastos * 100)) if total_gastos else 0,
            }
            for c in por_categoria
        ]

    clave_mes_actual = date.today().strftime("%Y-%m")
    gastado_mes = int(gastos_por_mes.get(clave_mes_actual, 0))
    if presupuesto_row:
        limite = float(presupuesto_row["monto_limite"])
        usado = int(round(gastado_mes / limite * 100)) if limite else 0
        datos["presupuesto"] = {
            "periodo": presupuesto_row["periodo"],
            "limite": _fmt(limite),
            "gastado": _fmt(gastado_mes),
            "disponible": _fmt(max(limite - gastado_mes, 0)),
            "usado": usado,
        }

    evolucion = []
    for d in _ultimos_meses(6):
        clave = d.strftime("%Y-%m")
        evolucion.append({
            "mes": MESES_ES[d.month - 1],
            "ingresos": int(ingresos_por_mes.get(clave, 0)),
            "gastos": int(gastos_por_mes.get(clave, 0)),
        })
    datos["evolucion"] = evolucion
    datos["hay_evolucion"] = any(e["ingresos"] or e["gastos"] for e in evolucion)

    datos["categorias_datos"] = [
        {"categoria": c["categoria"], "total": round(float(c["total"]))}
        for c in por_categoria
    ]

    return datos


# --- Presupuesto -------------------------------------------------------------

def get_presupuesto(usuario_id: int):
    """Presupuesto del mes vigente del estudiante (o None si no existe)."""
    estudiante_id = get_estudiante_id(usuario_id)
    if estudiante_id is None:
        return None

    inicio = date.today().replace(day=1)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, monto_limite, periodo, fecha_inicio, fecha_fin "
                "FROM presupuesto WHERE estudiante_id=%s AND fecha_inicio=%s "
                "ORDER BY id DESC LIMIT 1",
                (estudiante_id, inicio),
            )
            return cur.fetchone()
    finally:
        conn.close()


def guardar_presupuesto(usuario_id: int, monto) -> tuple:
    """Crea o actualiza el límite del mes vigente.

    RETORNA:
        (True, mensaje) o (False, mensaje).
    """
    try:
        valor = float(monto)
    except (TypeError, ValueError):
        return False, "Monto inválido."

    if valor <= 0:
        return False, "El monto debe ser mayor a cero."
    if valor > 9999999999.99:
        return False, "El monto excede el límite permitido."

    estudiante_id = get_estudiante_id(usuario_id)
    if estudiante_id is None:
        return False, "Tu cuenta aún no tiene perfil de estudiante."

    hoy = date.today()
    inicio = hoy.replace(day=1)
    siguiente = date(hoy.year + (hoy.month == 12), (hoy.month % 12) + 1, 1)
    fin = siguiente - timedelta(days=1)
    periodo = f"{MESES_LARGOS[hoy.month - 1]} {hoy.year}"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM presupuesto WHERE estudiante_id=%s AND fecha_inicio=%s "
                "ORDER BY id DESC LIMIT 1",
                (estudiante_id, inicio),
            )
            fila = cur.fetchone()
            if fila:
                cur.execute(
                    "UPDATE presupuesto SET monto_limite=%s, periodo=%s, fecha_fin=%s "
                    "WHERE id=%s",
                    (valor, periodo, fin, fila["id"]),
                )
                accion = "actualizado"
            else:
                cur.execute(
                    "INSERT INTO presupuesto "
                    "(monto_limite, periodo, fecha_inicio, fecha_fin, estudiante_id) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (valor, periodo, inicio, fin, estudiante_id),
                )
                accion = "definido"
        conn.commit()
    except pymysql.MySQLError:
        conn.rollback()
        logger.exception("No se pudo guardar el presupuesto del usuario %s", usuario_id)
        return False, "No fue posible guardar el presupuesto"
    finally:
        conn.close()

    return True, f"Presupuesto {accion} correctamente: {_fmt(valor)}."


# --- Registros (lista) -------------------------------------------------------

def get_registros_paginados(usuario_id: int, tipo: str = "", q: str = "",
                            pagina: int = 1, por_pagina: int = 10) -> dict:
    """Movimientos filtrados y paginados en MySQL.

    ``tipo`` debe ser "", "Ingreso" o "Gasto"; cualquier otro valor se ignora.
    ``q`` busca coincidencias en la descripción.
    """
    vacio = {
        "registros": [], "total": 0, "pagina": 1,
        "total_paginas": 1, "por_pagina": por_pagina,
    }
    estudiante_id = get_estudiante_id(usuario_id)
    if estudiante_id is None:
        return vacio

    tipo = tipo if tipo in ("Ingreso", "Gasto") else ""
    q = (q or "").strip()[:60]
    pagina = max(1, int(pagina or 1))
    por_pagina = max(1, min(int(por_pagina or 10), 100))
    offset = (pagina - 1) * por_pagina

    base = (
        "SELECT 'Ingreso' AS tipo, id, descripcion, monto, fecha "
        "FROM ingreso WHERE estudiante_id=%s "
        "UNION ALL "
        "SELECT 'Gasto' AS tipo, id, descripcion, monto, fecha "
        "FROM gasto WHERE estudiante_id=%s"
    )
    condiciones = []
    parametros = [estudiante_id, estudiante_id]
    if tipo:
        condiciones.append("t.tipo=%s")
        parametros.append(tipo)
    if q:
        condiciones.append("t.descripcion LIKE %s")
        parametros.append(f"%{q}%")
    where = (" WHERE " + " AND ".join(condiciones)) if condiciones else ""

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS total FROM ({base}) t{where}",
                tuple(parametros),
            )
            total = int(cur.fetchone()["total"])

            total_paginas = max(1, (total + por_pagina - 1) // por_pagina)
            if pagina > total_paginas:
                pagina = total_paginas
                offset = (pagina - 1) * por_pagina

            cur.execute(
                f"SELECT * FROM ({base}) t{where} "
                "ORDER BY t.fecha DESC, t.id DESC LIMIT %s OFFSET %s",
                tuple(parametros + [por_pagina, offset]),
            )
            filas = cur.fetchall()
    finally:
        conn.close()

    return {
        "registros": [_formatear_movimiento(f) for f in filas],
        "total": total,
        "pagina": pagina,
        "total_paginas": total_paginas,
        "por_pagina": por_pagina,
    }


def get_registros(usuario_id: int) -> list:
    """Compatibilidad: todos los movimientos del estudiante."""
    return get_registros_paginados(usuario_id, por_pagina=1000)["registros"]


def get_totales(usuario_id: int) -> dict:
    """Totales para las tarjetas de lista.html."""
    estudiante_id = get_estudiante_id(usuario_id)
    datos = {
        "total_ingresos": "$0",
        "total_gastos": "$0",
        "balance": "$0",
        "total_registros": 0,
    }
    if estudiante_id is None:
        return datos

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(SUM(monto),0) AS s FROM ingreso WHERE estudiante_id=%s",
                (estudiante_id,),
            )
            ingresos = float(cur.fetchone()["s"])

            cur.execute(
                "SELECT COALESCE(SUM(monto),0) AS s FROM gasto WHERE estudiante_id=%s",
                (estudiante_id,),
            )
            gastos = float(cur.fetchone()["s"])

            cur.execute(
                "SELECT (SELECT COUNT(*) FROM ingreso WHERE estudiante_id=%s) "
                "+ (SELECT COUNT(*) FROM gasto WHERE estudiante_id=%s) AS t",
                (estudiante_id, estudiante_id),
            )
            registros = int(cur.fetchone()["t"])
    finally:
        conn.close()

    datos["total_ingresos"] = _fmt(ingresos)
    datos["total_gastos"] = _fmt(gastos)
    datos["balance"] = _fmt(ingresos - gastos)
    datos["total_registros"] = registros
    return datos


def crear_registro(usuario_id: int, tipo: str, descripcion: str,
                   monto: float, categoria: str, fecha: str) -> tuple:
    """Guarda un movimiento nuevo (ingreso o gasto).

    RETORNA:
        (True, mensaje) o (False, mensaje).

    SEGURIDAD: el nombre de la tabla sale de un conjunto fijo (nunca del
    usuario) y los valores van por parámetros (%s), evitando inyección SQL.
    """
    estudiante_id = get_estudiante_id(usuario_id)
    if estudiante_id is None:
        return False, "Tu cuenta aún no tiene perfil de estudiante."

    # La tabla se selecciona de una lista blanca; los valores siguen parametrizados.
    tablas = {"Ingreso": "ingreso", "Gasto": "gasto"}
    tabla = tablas.get(tipo)
    if tabla is None:
        return False, "Tipo de movimiento inválido."

    monto = float(monto)
    if monto <= 0:
        return False, "El monto debe ser mayor a cero."

    if not fecha:
        fecha = date.today().isoformat()

    # El estudiante_id en el DELETE impide borrar registros de otra cuenta.
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {tabla} (monto, descripcion, categoria, fecha, estudiante_id) "
                "VALUES (%s, %s, %s, %s, %s)",
                (monto, descripcion, categoria, fecha, estudiante_id),
            )
        conn.commit()
    except pymysql.MySQLError:
        conn.rollback()
        logger.exception("No se pudo crear movimiento para usuario %s", usuario_id)
        return False, "No fue posible guardar el movimiento"
    finally:
        conn.close()

    return True, f"{tipo} de ${'{:,.0f}'.format(monto).replace(',', '.')} registrado correctamente."


def eliminar_registro(usuario_id: int, tipo: str, registro_id: int) -> tuple:
    """Borra un movimiento solo si pertenece al estudiante del usuario (protege
    contra borrado de datos ajenos)."""
    estudiante_id = get_estudiante_id(usuario_id)
    if estudiante_id is None:
        return False, "Tu cuenta aún no tiene perfil de estudiante."

    tablas = {"Ingreso": "ingreso", "Gasto": "gasto"}
    tabla = tablas.get(tipo)
    if tabla is None:
        return False, "Tipo de movimiento inválido."

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {tabla} WHERE id=%s AND estudiante_id=%s",
                (registro_id, estudiante_id),
            )
            afectadas = cur.rowcount
        conn.commit()
    except Exception:
        conn.rollback()
        return False, "No se pudo eliminar el registro."
    finally:
        conn.close()

    if afectadas == 0:
        return False, "El registro no existe o no te pertenece."
    return True, "Registro eliminado correctamente."


# --- Reportes -----------------------------------------------------------------

def get_reportes(usuario_id: int) -> list:
    """Últimos reportes persistidos del estudiante (tabla reporte)."""
    estudiante_id = get_estudiante_id(usuario_id)
    if estudiante_id is None:
        return []

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, tipo, fecha_generacion, total_ingresos, total_gastos "
                "FROM reporte WHERE estudiante_id=%s "
                "ORDER BY fecha_generacion DESC, id DESC LIMIT 20",
                (estudiante_id,),
            )
            return [
                {
                    "id": fila["id"],
                    "tipo": fila["tipo"],
                    "fecha": fila["fecha_generacion"].strftime("%d/%m/%Y %H:%M")
                    if fila["fecha_generacion"] else "",
                    "total_ingresos": _fmt(fila["total_ingresos"]),
                    "total_gastos": _fmt(fila["total_gastos"]),
                    "balance": _fmt(float(fila["total_ingresos"]) - float(fila["total_gastos"])),
                }
                for fila in cur.fetchall()
            ]
    finally:
        conn.close()


def generar_reporte(usuario_id: int, tipo: str) -> tuple:
    """Persiste un reporte usando el stored procedure sp_generar_reporte.

    RETORNA:
        (True, mensaje) o (False, mensaje).
    """
    estudiante_id = get_estudiante_id(usuario_id)
    if estudiante_id is None:
        return False, "Tu cuenta aún no tiene perfil de estudiante."

    tipo = (tipo or "").strip()[:50]
    if not tipo:
        return False, "Selecciona el tipo de reporte."

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # El procedure valida y calcula los totales dentro de MySQL.
            cur.callproc("sp_generar_reporte", (estudiante_id, tipo, 0))
            cur.execute("SELECT @p_reporte_id AS rid")
            fila = cur.fetchone()
        conn.commit()
        reporte_id = fila["rid"] if fila else None
    except pymysql.MySQLError:
        conn.rollback()
        logger.exception("No se pudo generar el reporte del usuario %s", usuario_id)
        return False, "No fue posible generar el reporte"
    finally:
        conn.close()

    return True, f"Reporte #{reporte_id} ({tipo}) generado correctamente."


def exportar_csv(usuario_id: int) -> str:
    """CSV con todos los movimientos del estudiante.

    La ruta añade un BOM UTF-8 para que Excel reconozca tildes y eñes.
    """
    buffer = io.StringIO()
    escritor = csv.writer(buffer, lineterminator="\r\n")
    escritor.writerow(["Tipo", "Descripcion", "Monto", "Fecha", "Categoria"])

    estudiante_id = get_estudiante_id(usuario_id)
    if estudiante_id is not None:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT tipo, descripcion, monto, fecha, categoria FROM ("
                    "  SELECT 'Ingreso' AS tipo, descripcion, monto, fecha, categoria "
                    "  FROM ingreso WHERE estudiante_id=%s "
                    "  UNION ALL "
                    "  SELECT 'Gasto' AS tipo, descripcion, monto, fecha, categoria "
                    "  FROM gasto WHERE estudiante_id=%s"
                    ") AS t ORDER BY t.fecha DESC",
                    (estudiante_id, estudiante_id),
                )
                for fila in cur.fetchall():
                    escritor.writerow([
                        fila["tipo"],
                        fila["descripcion"],
                        f"{float(fila['monto']):.2f}",
                        fila["fecha"].strftime("%Y-%m-%d %H:%M") if fila["fecha"] else "",
                        fila["categoria"],
                    ])
        finally:
            conn.close()

    return buffer.getvalue()


# --- Notificaciones ----------------------------------------------------------

def get_notificaciones(usuario_id: int) -> dict:
    """Avisos reales generados a partir de los datos del usuario.

    Reglas: 1) registro reciente, 2) presupuesto cerca/superado, 3) gasto
    elevado (>40% del mes), 4) buen/negativo manejo del mes.
    """
    vacio = {"notificaciones": [], "hay_notificaciones": False}

    estudiante_id = get_estudiante_id(usuario_id)
    if estudiante_id is None:
        return vacio

    # Las notificaciones se calculan al consultar; no se duplica información
    # derivada en una tabla adicional.
    avisos = []
    hoy = date.today()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT tipo, descripcion, monto, fecha FROM ("
                "  SELECT 'Ingreso' AS tipo, descripcion, monto, fecha "
                "  FROM ingreso WHERE estudiante_id=%s"
                "  UNION ALL"
                "  SELECT 'Gasto' AS tipo, descripcion, monto, fecha "
                "  FROM gasto WHERE estudiante_id=%s"
                ") AS t ORDER BY fecha DESC LIMIT 3",
                (estudiante_id, estudiante_id),
            )
            for m in cur.fetchall():
                fecha = m["fecha"]
                if isinstance(fecha, _dt_datetime):
                    fecha = fecha.date()
                dias = (hoy - fecha).days if fecha else None
                if dias is None:
                    continue
                cuando = "Hoy" if dias <= 0 else ("Ayer" if dias == 1 else f"Hace {dias} días")
                verbo = "un ingreso" if m["tipo"] == "Ingreso" else "un gasto"
                avisos.append({
                    "icono": "✅",
                    "clase": "exito",
                    "titulo": "Registro exitoso",
                    "mensaje": f"Registraste {verbo} de {_fmt(m['monto'])}: {m['descripcion']}.",
                    "tiempo": cuando,
                })

            clave_mes = hoy.strftime("%Y-%m")
            cur.execute(
                "SELECT descripcion, monto FROM gasto "
                "WHERE estudiante_id=%s AND DATE_FORMAT(fecha,'%%Y-%%m')=%s "
                "ORDER BY monto DESC LIMIT 1",
                (estudiante_id, clave_mes),
            )
            gasto_top = cur.fetchone()

            cur.execute(
                "SELECT COALESCE(SUM(monto),0) AS s FROM gasto "
                "WHERE estudiante_id=%s AND DATE_FORMAT(fecha,'%%Y-%%m')=%s",
                (estudiante_id, clave_mes),
            )
            gastado_mes = float(cur.fetchone()["s"])

            cur.execute(
                "SELECT COALESCE(SUM(monto),0) AS s FROM ingreso "
                "WHERE estudiante_id=%s AND DATE_FORMAT(fecha,'%%Y-%%m')=%s",
                (estudiante_id, clave_mes),
            )
            ingresos_mes = float(cur.fetchone()["s"])

            cur.execute(
                "SELECT monto_limite FROM presupuesto WHERE estudiante_id=%s "
                "ORDER BY fecha_inicio DESC LIMIT 1",
                (estudiante_id,),
            )
            fila_presupuesto = cur.fetchone()
    finally:
        conn.close()

    if fila_presupuesto and gastado_mes > 0:
        limite = float(fila_presupuesto["monto_limite"])
        if limite > 0:
            porcentaje = int(round(gastado_mes / limite * 100))
            if porcentaje >= 100:
                avisos.append({
                    "icono": "❌", "clase": "error",
                    "titulo": "Presupuesto superado",
                    "mensaje": f"Gastaste {_fmt(gastado_mes)} de tus {_fmt(limite)} este mes ({porcentaje}%).",
                    "tiempo": "Este mes",
                })
            elif porcentaje >= 80:
                avisos.append({
                    "icono": "⚠️", "clase": "advertencia",
                    "titulo": "Estás cerca del límite",
                    "mensaje": f"Ya usaste el {porcentaje}% de tu presupuesto mensual.",
                    "tiempo": "Este mes",
                })

    if gasto_top and gastado_mes > 0 and float(gasto_top["monto"]) >= gastado_mes * 0.4:
        avisos.append({
            "icono": "💸", "clase": "alerta",
            "titulo": "Gasto elevado detectado",
            "mensaje": f"'{gasto_top['descripcion']}' fue de {_fmt(gasto_top['monto'])}, "
                       f"el {int(round(float(gasto_top['monto']) / gastado_mes * 100))}% de lo gastado este mes.",
            "tiempo": "Este mes",
        })

    if ingresos_mes > gastado_mes and (ingresos_mes or gastado_mes):
        avisos.append({
            "icono": "🎯", "clase": "exito",
            "titulo": "Buen manejo este mes",
            "mensaje": f"Tus ingresos ({_fmt(ingresos_mes)}) superan tus gastos ({_fmt(gastado_mes)}). ¡Sigue así!",
            "tiempo": "Este mes",
        })
    elif gastado_mes > ingresos_mes and ingresos_mes >= 0 and gastado_mes > 0:
        avisos.append({
            "icono": "ℹ️", "clase": "informacion",
            "titulo": "Vas en negativo este mes",
            "mensaje": f"Hasta ahora gastas {_fmt(gastado_mes)} y has recibido {_fmt(ingresos_mes)}.",
            "tiempo": "Este mes",
        })

    return {"notificaciones": avisos[:6], "hay_notificaciones": bool(avisos)}