"""=============================================================
FinovaTech v10 - Blueprint público de recuperación de contraseña
=============================================================="""

import logging

from flask import Blueprint, render_template, request, url_for

from app.correo import enviar_correo_recuperacion
from app.modelos.bitacora import registrar_acceso
from app.modelos.recuperacion import (
    buscar_usuario_por_email,
    crear_token_recuperacion,
    restablecer_password,
    validar_token,
)

logger = logging.getLogger(__name__)

recuperacion_bp = Blueprint("recuperacion", __name__)

MENSAJE_GENERICO = (
    "Si el correo está registrado, enviamos un enlace para restablecer la "
    "contraseña. Revisa tu bandeja o el log del servidor en modo local."
)


@recuperacion_bp.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    """Solicita un enlace sin revelar si la cuenta existe."""
    mensaje = None
    if request.method == "POST":
        correo = request.form.get("email", "").strip().lower()
        ip = request.remote_addr or "desconocida"
        usuario = buscar_usuario_por_email(correo) if correo else None

        if usuario:
            token = crear_token_recuperacion(usuario["id"], ip)
            if token:
                enlace = url_for("recuperacion.restablecer", token=token, _external=True)
                try:
                    enviar_correo_recuperacion(usuario["email"], enlace)
                except Exception:
                    logger.exception("No se pudo enviar el correo de recuperación")
                registrar_acceso(
                    usuario["id"], usuario["email"], "recuperacion_solicitada",
                    ip, "Enlace de recuperación generado",
                )
        mensaje = MENSAJE_GENERICO

    return render_template("recuperar.html", mensaje=mensaje)


@recuperacion_bp.route("/restablecer/<token>", methods=["GET", "POST"])
def restablecer(token):
    """Valida el token y permite cambiar la contraseña una sola vez."""
    usuario = validar_token(token)
    error = None
    exito = None

    if not usuario:
        return render_template(
            "restablecer.html",
            token=token,
            error="El enlace no es válido o ya expiró. Solicita uno nuevo.",
        )

    if request.method == "POST":
        ok, mensaje = restablecer_password(
            token,
            request.form.get("nueva", ""),
            request.form.get("confirmar", ""),
        )
        if ok:
            exito = mensaje
            registrar_acceso(
                usuario["id"], usuario["email"], "recuperacion_completada",
                request.remote_addr or "desconocida", "Contraseña restablecida",
            )
            usuario = None
        else:
            error = mensaje

    return render_template(
        "restablecer.html",
        token=token,
        usuario=usuario,
        error=error,
        exito=exito,
    )
