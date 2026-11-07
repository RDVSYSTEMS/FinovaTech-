"""=============================================================
FinovaTech v10 - Blueprint de bitácora de accesos (admin)
=============================================================="""

from flask import Blueprint, render_template

from app.modelos.bitacora import get_accesos
from app.seguridad import rol_requerido

bitacora_bp = Blueprint("bitacora", __name__)


@bitacora_bp.route("/bitacora")
@rol_requerido("administrador")
def bitacora():
    """Muestra los últimos 100 eventos de autenticación."""
    return render_template("bitacora.html", accesos=get_accesos(100))
