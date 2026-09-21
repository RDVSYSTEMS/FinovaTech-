"""=============================================================
FinovaTech v9 - Seguridad
==============================================================
Módulo transversal de seguridad de la aplicación:

  - Protección CSRF global (token por sesión, comparación
    segura con hmac.compare_digest).
  - Cabeceras HTTP de seguridad para todas las respuestas.
  - Decorador login_requerido para rutas protegidas.
  - Límite de intentos de login (anti fuerza bruta).

Las reglas de negocio (roles permitidos, validaciones) se
mantienen en cada blueprint que las necesita.
=============================================================="""

import hmac
import secrets

from datetime import datetime, timedelta
from functools import wraps

from flask import redirect, request, session, url_for

# --- CSRF -------------------------------------------------------------------

def csrf_proteger():
    """Genera el token en GET y valida el token en POST (todas las rutas)."""
    if request.method in ("GET", "HEAD"):
        # El token se crea una vez por sesión y se reutiliza en los formularios.
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_hex(32)
        return None

    # El token viaja en formularios HTML; hmac evita comparaciones temporizadas.
    token_sesion = session.get("_csrf", "")
    token_formulario = request.form.get("csrf_token", "")
    if not token_sesion or not hmac.compare_digest(token_sesion, token_formulario):
        return (
            "Petición bloqueada: falta el token de seguridad (CSRF). "
            "Vuelve atrás, recarga la página e inténtalo de nuevo.",
            400,
        )


def inyectar_csrf():
    """Hace disponible {{ csrf_token }} en todas las plantillas."""
    # El context processor evita repetir la lectura de sesión en cada template.
    return {"csrf_token": session.get("_csrf", "")}


# --- Rutas protegidas -------------------------------------------------------

def login_requerido(func):
    """Exige sesión activa; si no hay, redirige al login."""

    @wraps(func)
    def envoltura(*args, **kwargs):
        # Se usa user_email como indicador de sesión autenticada.
        if "user_email" not in session:
            return redirect(url_for("publicas.login"))
        return func(*args, **kwargs)

    return envoltura


# --- Límite de intentos de login (anti fuerza bruta) ------------------------

MAX_INTENTOS_LOGIN = 5
BLOQUEO_BASE_SEGUNDOS = 120
_intentos_login = {}


def verificar_bloqueo(ip: str, correo: str):
    """Devuelve True si la combinación ip|correo está bloqueada en este momento."""
    datos = _intentos_login.get(f"{ip}|{correo}")
    return bool(datos and datos[1] and datetime.now() < datos[1])


def segundos_restantes_bloqueo(ip: str, correo: str) -> int:
    """Segundos que faltan para que se levante el bloqueo actual (0 si no hay)."""
    datos = _intentos_login.get(f"{ip}|{correo}")
    if not datos or not datos[1]:
        return 0
    return int((datos[1] - datetime.now()).total_seconds()) + 1


def registrar_fallo(ip: str, correo: str):
    """Suma un intento fallido y activa/crece el bloqueo cuando corresponde."""
    clave = f"{ip}|{correo}"
    datos = _intentos_login.get(clave)
    fallos = (datos[0] if datos else 0) + 1
    bloqueado_hasta = None
    if fallos >= MAX_INTENTOS_LOGIN:
        # Cada nueva ronda multiplica por dos el tiempo de bloqueo.
        rondas = fallos // MAX_INTENTOS_LOGIN
        bloqueado_hasta = datetime.now() + timedelta(
            seconds=BLOQUEO_BASE_SEGUNDOS * (2 ** (rondas - 1))
        )
    _intentos_login[clave] = [fallos, bloqueado_hasta, datetime.now()]

    if len(_intentos_login) > 5000:
        # Limpia entradas antiguas para evitar crecimiento indefinido en memoria.
        limite = datetime.now() - timedelta(hours=1)
        for k in [k for k, v in _intentos_login.items() if v[2] < limite]:
            _intentos_login.pop(k, None)


def limpiar_fallos(ip: str, correo: str):
    """Borra el historial de fallos de una combinación tras un login exitoso."""
    _intentos_login.pop(f"{ip}|{correo}", None)


# --- Cabeceras HTTP de seguridad --------------------------------------------

CABECERAS_SEGURIDAD = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data:; "
        "media-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    ),
}


def cabeceras_seguridad(respuesta):
    """Añade políticas defensivas comunes a todas las respuestas HTTP."""
    # setdefault respeta una cabecera definida explícitamente por Flask o por
    # otro middleware de la aplicación.
    for nombre, valor in CABECERAS_SEGURIDAD.items():
        respuesta.headers.setdefault(nombre, valor)
    if request.is_secure:
        respuesta.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
    return respuesta