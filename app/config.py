"""=============================================================
FinovaTech v9 - Configuración de la aplicación
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
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "finovatech")

    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError(
            "Falta SECRET_KEY. Crea el archivo .env (copia .env.example) con "
            "una SECRET_KEY aleatoria: "
            'python -c "import secrets; print(secrets.token_hex(32))"'
        )