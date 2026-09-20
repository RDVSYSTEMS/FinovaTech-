"""=============================================================
FinovaTech v9 - Blueprint del panel (protegido)
=============================================================="""

from flask import Blueprint, render_template, session

from app.modelos.finanzas import get_datos_panel
from app.seguridad import login_requerido

panel_bp = Blueprint("panel", __name__)


@panel_bp.route("/panel")
@login_requerido
def panel():
    datos = get_datos_panel(session["user_id"])
    return render_template("panel.html", **datos)