"""=============================================================
FinovaTech v9 - Blueprint de notificaciones y agendamiento
=============================================================="""

from flask import Blueprint, jsonify, render_template, request, session

from app.modelos.agendamientos import crear_agendamiento
from app.modelos.finanzas import get_notificaciones
from app.seguridad import login_requerido

notificaciones_bp = Blueprint("notificaciones", __name__)


@notificaciones_bp.route("/notificacion")
@login_requerido
def notificacion():
    """Renderiza las notificaciones calculadas para el usuario."""
    datos = get_notificaciones(session["user_id"])
    return render_template("notificacion.html", **datos)


@notificaciones_bp.route("/agendamiento", methods=["GET", "POST"])
@login_requerido
def agendamiento():
    """Muestra el formulario o guarda una sesión de educación financiera."""
    if request.method == "POST":
        exito, mensaje = crear_agendamiento(
            session["user_id"],
            request.form.get("fecha", "").strip(),
            request.form.get("hora", "").strip(),
            request.form.get("categoria", "").strip(),
            request.form.get("estado", "pendiente").strip(),
            request.form.get("comentarios", "").strip(),
        )
        return jsonify(ok=exito, mensaje=mensaje), (200 if exito else 400)

    return render_template("agendamiento.html")