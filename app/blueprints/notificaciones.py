"""=============================================================
FinovaTech v9 - Blueprint de notificaciones y agendamiento
=============================================================="""

from flask import Blueprint, render_template, session

from app.modelos.finanzas import get_notificaciones
from app.seguridad import login_requerido

notificaciones_bp = Blueprint("notificaciones", __name__)


@notificaciones_bp.route("/notificacion")
@login_requerido
def notificacion():
    datos = get_notificaciones(session["user_id"])
    return render_template("notificacion.html", **datos)


@notificaciones_bp.route("/agendamiento")
@login_requerido
def agendamiento():
    return render_template("agendamiento.html")