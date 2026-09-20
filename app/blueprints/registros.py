"""=============================================================
FinovaTech v9 - Blueprint de registros (lista + alta/borrado)
=============================================================="""

from urllib.parse import quote

from flask import Blueprint, redirect, render_template, request, session, url_for

from app.modelos.finanzas import (crear_registro, eliminar_registro, get_registros, get_totales)
from app.seguridad import login_requerido

registros_bp = Blueprint("registros", __name__)


@registros_bp.route("/lista")
@login_requerido
def lista():
    registros = get_registros(session["user_id"])
    totales = get_totales(session["user_id"])
    return render_template("lista.html", registros=registros, **totales)


@registros_bp.route("/registro/nuevo", methods=["POST"])
@login_requerido
def registro_nuevo():
    tipo = request.form.get("tipo", "")
    descripcion = request.form.get("descripcion", "").strip()
    monto = request.form.get("monto", "").strip()
    categoria = request.form.get("categoria", "").strip()
    fecha = request.form.get("fecha", "") or None

    if not all([tipo, descripcion, monto, categoria]):
        return redirect(url_for("registros.lista") + "?error=" + quote("Completa todos los campos"))

    monto_limpio = monto.replace("$", "").replace(".", "").replace(",", ".")
    try:
        monto_valor = float(monto_limpio)
    except ValueError:
        return redirect(url_for("registros.lista") + "?error=" + quote("Monto inválido"))

    exito, mensaje = crear_registro(
        session["user_id"], tipo, descripcion, monto_valor, categoria, fecha
    )
    clave = "ok" if exito else "error"
    return redirect(url_for("registros.lista") + f"?{clave}=" + quote(mensaje))


@registros_bp.route("/registro/eliminar/<tipo>/<int:registro_id>", methods=["POST"])
@login_requerido
def registro_eliminar(tipo, registro_id):
    exito, mensaje = eliminar_registro(session["user_id"], tipo, registro_id)
    clave = "ok" if exito else "error"
    return redirect(url_for("registros.lista") + f"?{clave}=" + quote(mensaje))