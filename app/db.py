"""=============================================================
FinovaTech v9 - Acceso a la base de datos (MySQL vía XAMPP)
==============================================================
get_connection() abre una conexión nueva a MySQL usando PyMySQL
y devuelve las filas como diccionarios (DictCursor).
=============================================================="""

import pymysql

from app.config import Config


def get_connection():
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )