"""=============================================================
FinovaTech v10 - Páginas públicas (inicio, login, registro, logout)
=============================================================="""

import secrets

from flask import Blueprint, redirect, render_template, request, session, url_for
from jinja2 import TemplateNotFound

from app.db import get_connection
from app.modelos.bitacora import registrar_acceso
from app.modelos.usuarios import registrar_usuario, verificar_login
from app.seguridad import (limpiar_fallos, registrar_fallo, segundos_restantes_bloqueo, verificar_bloqueo)

publicas_bp = Blueprint("publicas", __name__)

# Lista blanca: el público solo puede crear cuentas con estos roles.
ROLES_PERMITIDOS = {"estudiante", "padre"}


def _contar_usuarios() -> int:
    """Cuenta las cuentas registradas para la estadística de la portada."""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS total FROM usuario")
                return int(cur.fetchone()["total"])
        finally:
            conn.close()
    except Exception:
        return 0


def _contar_movimientos() -> int:
    """Cuenta ingresos y gastos totales para la estadística de la portada."""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT (SELECT COUNT(*) FROM ingreso) + (SELECT COUNT(*) FROM gasto) AS total"
                )
                return int(cur.fetchone()["total"])
        finally:
            conn.close()
    except Exception:
        return 0


def _contar_categorias() -> int:
    """Cuenta las categorías de gasto realmente registradas."""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(DISTINCT categoria) AS total FROM gasto")
                return int(cur.fetchone()["total"])
        finally:
            conn.close()
    except Exception:
        return 0


@publicas_bp.route("/")
def index():
    """Renderiza la página pública de inicio."""
    return render_template(
        "index.html",
        total_usuarios=_contar_usuarios(),
        total_movimientos=_contar_movimientos(),
        total_categorias=_contar_categorias(),
    )


@publicas_bp.route("/login", methods=["GET", "POST"])
def login():
    """Autentica al usuario y rota la sesión al iniciar correctamente."""
    error_message = None

    if request.method == "POST":
        ip = request.remote_addr or "desconocida"
        correo = request.form.get("email", "").strip().lower()

        if verificar_bloqueo(ip, correo):
            espera = segundos_restantes_bloqueo(ip, correo)
            registrar_acceso(None, correo, "bloqueo", ip, "Intento durante bloqueo")
            error_message = (
                "Demasiados intentos fallidos. Espera "
                + str(espera)
                + " segundos antes de volver a intentar."
            )
            return render_template("login.html", error_message=error_message)

        email = request.form.get("email", "")
        password = request.form.get("password", "")

        user = verificar_login(email, password)

        if user:
            limpiar_fallos(ip, correo)
            registrar_acceso(user["id"], user["email"], "login_ok", ip, f"Rol {user['rol']}")
            # Rota la sesión (previene fijación de sesión) y renueva el CSRF.
            session.clear()
            session["_csrf"] = secrets.token_hex(32)

            session["user_id"] = user["id"]
            session["user_email"] = user["email"]
            session["user_name"] = user["nombre"]
            session["user_type"] = user["rol"]
            if user["rol"] == "padre":
                return redirect(url_for("supervision.supervision"))
            return redirect(url_for("panel.panel"))

        registrar_fallo(ip, correo)
        registrar_acceso(None, correo, "login_fallido", ip, "Credenciales incorrectas")
        if verificar_bloqueo(ip, correo):
            registrar_acceso(None, correo, "bloqueo", ip, "Se alcanzó el máximo de fallos")
        error_message = "Correo o contraseña incorrectos"

    return render_template("login.html", error_message=error_message)


@publicas_bp.route("/registro", methods=["GET", "POST"])
def registro():
    """Valida y crea cuentas públicas con roles permitidos."""
    error_message = None
    success_message = None

    if request.method == "POST":
        nombre = request.form.get("full_name", "")
        email = request.form.get("email", "")
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        rol = request.form.get("user_type", "")

        if not all([nombre, email, username, password, rol]):
            error_message = "Completa todos los campos"
        elif rol not in ROLES_PERMITIDOS:
            error_message = "Tipo de cuenta no permitido"
        elif len(password) < 8:
            error_message = "La contraseña debe tener mínimo 8 caracteres"
        elif password != confirm_password:
            error_message = "Las contraseñas no coinciden"
        else:
            exito, mensaje = registrar_usuario(nombre, email, username, password, rol)
            if exito:
                success_message = mensaje
            else:
                error_message = mensaje

    return render_template(
        "registro.html",
        error_message=error_message,
        success_message=success_message,
    )


@publicas_bp.route("/logout", methods=["POST"])
def logout():
    """Elimina toda la sesión activa y vuelve al inicio."""
    if session.get("user_email"):
        registrar_acceso(
            session.get("user_id"),
            session.get("user_email"),
            "logout",
            request.remote_addr or "desconocida",
            "Cierre de sesión",
        )
    session.clear()
    return redirect(url_for("publicas.index"))


# Páginas públicas con enlace a ".html" (contacto, servicios, soporte...)
PAGINAS_PUBLICAS_HTML = {"contacto", "servicios", "soporte", "terminos", "login", "registro", "index"}


@publicas_bp.route("/<page>.html")
def render_html_page(page):
    """Sirve para aliarse .html sin permitir plantillas arbitrarias."""
    if page in PAGINAS_PUBLICAS_HTML:
        try:
            if page == "login":
                return login()
            if page == "registro":
                return registro()
            if page == "index":
                return index()
            return render_template(f"{page}.html")
        except TemplateNotFound:
            return redirect(url_for("publicas.index"))
    return redirect(url_for("publicas.index"))