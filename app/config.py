"""=============================================================
FinovaTech v10 - Configuración de la aplicación
==============================================================
Centraliza los datos de conexión a MySQL (XAMPP) y la clave
secreta de sesión, cargados desde el archivo ".env".

Variables de entorno usadas:
  DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, SECRET_KEY
=============================================================="""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Agrupa la configuración de Flask, MySQL, correo y sesiones desde .env."""

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "finovatech")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"

    # Correo saliente para recuperación de contraseña (opcional en local).
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "1") == "1"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "0") == "1"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM = os.getenv("MAIL_FROM") or MAIL_USERNAME or "no-reply@finovatech.local"
    PASSWORD_RESET_MINUTES = int(os.getenv("PASSWORD_RESET_MINUTES", "30"))

    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError(
            "Falta SECRET_KEY. Crea el archivo .env (copia .env.example) con "
            "una SECRET_KEY aleatoria: "
            'python -c "import secrets; print(secrets.token_hex(32))"'
        )