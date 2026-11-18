"""=============================================================
FinovaTech v10 - Punto de entrada del servidor
==============================================================
Uso:  python run.py

Para desarrollo con recarga automática: pon FLASK_DEBUG=1 en .env.
En producción mantenlo apagado (no expongas el depurador).
HOST permite escuchar en 0.0.0.0 (por defecto 127.0.0.1).
=============================================================="""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    debug_activado = os.getenv("FLASK_DEBUG", "0") == "1"
    puerto = int(os.getenv("PORT", "5001"))
    host = os.getenv("HOST", "127.0.0.1")
    app.run(debug=debug_activado, host=host, port=puerto)