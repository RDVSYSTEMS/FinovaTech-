"""=============================================================
FinovaTech v9 - Fábrica de la aplicación (Application Factory)
==============================================================
La función create_app() construye la aplicación Flask, registra
los blueprints y activa la seguridad global (CSRF + cabeceras).

RUTAS (URLs) principales:
  /                        -> Página principal (inicio)
  /login       GET/POST    -> Formulario / validación de credenciales
  /registro    GET/POST    -> Formulario / creación de cuenta
  /logout                  -> Cierra la sesión
  /panel                   -> Panel del usuario (protegida)
  /lista                   -> Lista de movimientos (protegida)
  /registro/nuevo  POST    -> Guarda un ingreso o gasto (protegida)
  /registro/eliminar/<tipo>/<id> POST -> Borra un movimiento (protegida)
  /notificacion            -> Centro de notificaciones (protegida)
  /<pagina>.html           -> Resto de páginas (contacto, soporte...)
=============================================================="""

from flask import Flask

from app.config import Config


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.secret_key = Config.SECRET_KEY

    # Cookie de sesión segura (HttpOnly + SameSite=Lax ayuda contra XSS/CSRF)
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    # Registro de blueprints (cada uno conserva las URLs de v8)
    from app.blueprints.publicas import publicas_bp
    from app.blueprints.panel import panel_bp
    from app.blueprints.registros import registros_bp
    from app.blueprints.notificaciones import notificaciones_bp

    app.register_blueprint(publicas_bp)
    app.register_blueprint(panel_bp)
    app.register_blueprint(registros_bp)
    app.register_blueprint(notificaciones_bp)

    # Seguridad global
    from app import seguridad

    app.before_request(seguridad.csrf_proteger)
    app.context_processor(seguridad.inyectar_csrf)
    app.after_request(seguridad.cabeceras_seguridad)

    return app