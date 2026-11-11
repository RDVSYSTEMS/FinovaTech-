"""=============================================================
FinovaTech v10 - Blueprint de supervisión (rol padre)
=============================================================="""

from urllib.parse import quote

from flask import Blueprint, redirect, render_template, request, session, url_for

from app.modelos.finanzas import get_datos_panel
from app.modelos.supervision import (
    desvincular_estudiante,
    get_estudiantes_vinculados,
    vincular_por_codigo,
)
from app.seguridad import rol_requerido

supervision_bp = Blueprint("supervision", __name__)


def _volver(clave: str, mensaje: str):
    """Redirige a supervisión mostrando el resultado de la operación."""
    return redirect(url_for("supervision.supervision") + f"?{clave}=" + quote(mensaje))


@supervision_bp.route("/supervision")
@rol_requerido("padre")
def supervision():
    """Vista de solo lectura de los estudiantes vinculados al padre."""
    estudiantes = []
    for fila in get_estudiantes_vinculados(session["user_id"]):
        estudiantes.append({
            "id": fila["id"],
            "nombre": fila["nombre"],
            "email": fila["email"],
            "username": fila["username"],
            "datos": get_datos_panel(fila["id"]),
        })
    return render_template("supervision.html", estudiantes=estudiantes)


@supervision_bp.route("/supervision/vincular", methods=["POST"])
@rol_requerido("padre")
def vincular():
    """Vincula un estudiante usando el código que él comparte."""
    exito, mensaje = vincular_por_codigo(
        session["user_id"], request.form.get("codigo", "")
    )
    return _volver("ok" if exito else "error", mensaje)


@supervision_bp.route("/supervision/desvincular/<int:estudiante_id>", methods=["POST"])
@rol_requerido("padre")
def desvincular(estudiante_id):
    """Elimina un vínculo propio del padre autenticado."""
    exito, mensaje = desvincular_estudiante(session["user_id"], estudiante_id)
    return _volver("ok" if exito else "error", mensaje)
