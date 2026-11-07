"""=============================================================
FinovaTech v10 - Blueprint del perfil de usuario (protegido)
============================================================="""

from urllib.parse import quote

from flask import Blueprint, redirect, render_template, request, session, url_for

from app.modelos.supervision import obtener_o_crear_codigo_vinculacion
from app.modelos.usuarios import (
    actualizar_datos_usuario,
    cambiar_password_usuario,
    get_usuario_por_id,
)
from app.seguridad import login_requerido

perfil_bp = Blueprint("perfil", __name__)


def _volver_al_perfil(clave: str, mensaje: str):
    """Redirige al perfil conservando el resultado de la operación."""
    return redirect(url_for("perfil.perfil") + f"?{clave}=" + quote(mensaje))


@perfil_bp.route("/perfil")
@login_requerido
def perfil():
    """Muestra los datos de la cuenta y los formularios de edición."""
    datos = get_usuario_por_id(session["user_id"])
    if not datos:
        session.clear()
        return redirect(url_for("publicas.login"))

    codigo = None
    if datos["rol"] == "estudiante":
        codigo = obtener_o_crear_codigo_vinculacion(datos["id"])
    return render_template("perfil.html", perfil=datos, codigo_vinculacion=codigo)


@perfil_bp.route("/perfil", methods=["POST"])
@login_requerido
def actualizar_perfil():
    """Actualiza nombre y nombre de usuario de la cuenta activa."""
    nombre = request.form.get("nombre", "")
    username = request.form.get("username", "")
    exito, mensaje = actualizar_datos_usuario(session["user_id"], nombre, username)

    if exito:
        session["user_name"] = nombre.strip()

    return _volver_al_perfil("ok" if exito else "error", mensaje)


@perfil_bp.route("/perfil/password", methods=["POST"])
@login_requerido
def actualizar_password():
    """Cambia la contraseña verificando la contraseña actual."""
    exito, mensaje = cambiar_password_usuario(
        session["user_id"],
        request.form.get("actual", ""),
        request.form.get("nueva", ""),
        request.form.get("confirmar", ""),
    )
    return _volver_al_perfil("ok" if exito else "error", mensaje)
