"""=============================================================
FinovaTech v10 - Blueprint del panel (protegido)
============================================================="""

from urllib.parse import quote

from flask import Blueprint, redirect, render_template, request, session, url_for

from app.modelos.finanzas import (
    get_datos_panel,
    get_presupuesto,
    guardar_presupuesto,
)
from app.seguridad import login_requerido

panel_bp = Blueprint("panel", __name__)


@panel_bp.route("/panel")
@login_requerido
def panel():
    """Consulta y entrega al template el resumen financiero del usuario."""
    datos = get_datos_panel(session["user_id"])
    return render_template("panel.html", **datos)


@panel_bp.route("/presupuesto", methods=["GET", "POST"])
@login_requerido
def presupuesto():
    """Define o actualiza el límite de gasto del mes vigente."""
    if request.method == "POST":
        monto = request.form.get("monto", "").strip()
        monto_limpio = monto.replace("$", "").replace(".", "").replace(",", ".")
        exito, mensaje = guardar_presupuesto(session["user_id"], monto_limpio)
        clave = "ok" if exito else "error"
        return redirect(url_for("panel.presupuesto") + f"?{clave}=" + quote(mensaje))

    datos = get_datos_panel(session["user_id"])
    actual = get_presupuesto(session["user_id"])
    limite_actual = int(float(actual["monto_limite"])) if actual else ""
    return render_template(
        "presupuesto.html",
        **datos,
        limite_actual=limite_actual,
    )
