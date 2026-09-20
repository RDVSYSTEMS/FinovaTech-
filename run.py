"""=============================================================
FinovaTech v9 - Punto de entrada del servidor
==============================================================
Uso:  python run.py

Para desarrollo con recarga automática: pon FLASK_DEBUG=1 en .env.
En producción mantenlo apagado (no expongas el depurador).
=============================================================="""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    debug_activado = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_activado, port=5000)