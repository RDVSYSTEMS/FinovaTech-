"""=============================================================
FinovaTech v9 - Modelo financiero (datos, registros, notificaciones)
==============================================================
Consulta la base de datos para el panel, la lista de movimientos
y las notificaciones de un usuario.

Tablas usadas (esquema finovatech): usuario, estudiante, ingreso,
gasto, presupuesto.

Formato de dinero: _fmt() convierte 440000 en "$440.000"
(estilo colombiano, con puntos de miles).
=============================================================="""

from datetime import date, datetime as _dt_datetime

from app.db import get_connection

MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def _fmt(valor) -> str:
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
            "usado": min(usado, 100),
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


# --- Registros (lista) -------------------------------------------------------

def get_registros(usuario_id: int) -> list:
    """Todos los movimientos del estudiante, del más reciente al más antiguo."""
    estudiante_id = get_estudiante_id(usuario_id)
    if estudiante_id is None:
        return []

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 'Ingreso' AS tipo, id, descripcion, monto, fecha "
                "FROM ingreso WHERE estudiante_id=%s "
                "UNION ALL "
                "SELECT 'Gasto' AS tipo, id, descripcion, monto, fecha "
                "FROM gasto WHERE estudiante_id=%s "
                "ORDER BY fecha DESC, id DESC",
                (estudiante_id, estudiante_id),
            )
            filas = cur.fetchall()
    finally:
        conn.close()

    return [_formatear_movimiento(f) for f in filas]


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

    tablas = {"Ingreso": "ingreso", "Gasto": "gasto"}
    tabla = tablas.get(tipo)
    if tabla is None:
        return False, "Tipo de movimiento inválido."

    monto = float(monto)
    if monto <= 0:
        return False, "El monto debe ser mayor a cero."

    if not fecha:
        fecha = date.today().isoformat()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {tabla} (monto, descripcion, categoria, fecha, estudiante_id) "
                "VALUES (%s, %s, %s, %s, %s)",
                (monto, descripcion, categoria, fecha, estudiante_id),
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return False, f"No se pudo guardar: {e}"
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