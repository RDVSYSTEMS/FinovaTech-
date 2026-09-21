"""=============================================================================
FinovaTech v9 — Datos de prueba (demo)
===============================================================================
Este script crea TODO lo necesario para que el panel del usuario demo se vea
lleno de datos reales apenas inicies sesión:

  1. Crea (si no existe) la cuenta de prueba:
       Correo:    adminr123@gmail.com
       Contraseña: 123456789

  2. Crea el perfil de ESTUDIANTE de esa cuenta.

  3. Inserta algunos INGRESOS y GASTOS de ejemplo, y un PRESUPUESTO mensual.

Este script no crea agendamientos: las citas pertenecen al flujo real del
usuario y deben registrarse desde la pantalla de agendamiento.

CÓMO SE EJECUTA (desde la carpeta del proyecto):
    python -m scripts.seed_demo

NOTA: el script es REPETIBLE. Si lo vuelves a ejecutar, limpia los datos de
ejemplo antiguos y los vuelve a crear, sin duplicarlos.
============================================================================="""

# ---------------------------------------------------------------------------
# IMPORTACIONES
#   - get_connection: para abrir conexiones a MySQL y hacer operaciones SQL.
#   - registrar_usuario: para crear la cuenta demo con contraseña cifrada.
# ---------------------------------------------------------------------------
from app.db import get_connection
from app.modelos.usuarios import registrar_usuario

# ---------------------------------------------------------------------------
# DATOS DEMO
#   Credenciales del usuario de demostración (coinciden con el README) y los
#   movimientos de ejemplo que se insertarán en las tablas ingreso y gasto.
# ---------------------------------------------------------------------------

# Cuenta de demostración
DEMO = {
    "nombre": "Administrador Demo",
    "email": "adminr123@gmail.com",
    "username": "adminrdv",
    "password": "123456789",
    "rol": "administrador",
}

# Ingresos de ejemplo: (meses_antes, descripción, monto en pesos)
#   meses_antes = 0  -> el mes actual
#   meses_antes = 5  -> hace 5 meses
# Con datos repartidos en los últimos 6 meses la gráfica de "Evolución
# financiera" del panel se ve con una curva realista y creciente.
INGRESOS = [
    (5, "Mesada", 230000),
    (4, "Mesada", 240000),
    (3, "Mesada", 250000),
    (3, "Premio académico", 35000),
    (2, "Mesada", 260000),
    (2, "Premio académico", 40000),
    (1, "Mesada", 270000),
    (1, "Trabajo fin de semana", 60000),
    (0, "Mesada", 280000),
    (0, "Premio académico", 40000),
    (0, "Trabajo fin de semana", 120000),
]

# Gastos de ejemplo: (meses_antes, descripción, categoría, monto en pesos)
GASTOS = [
    (5, "Útiles escolares", "Educación", 30000),
    (5, "Transporte", "Transporte", 35000),
    (4, "Comidas", "Alimentación", 40000),
    (4, "Entretenimiento", "Ocio", 25000),
    (3, "Transporte", "Transporte", 40000),
    (3, "Comidas", "Alimentación", 45000),
    (2, "Ahorro personal", "Ahorro", 30000),
    (2, "Comidas", "Alimentación", 50000),
    (2, "Útiles escolares", "Educación", 25000),
    (1, "Entretenimiento", "Ocio", 30000),
    (1, "Transporte", "Transporte", 40000),
    (1, "Comidas", "Alimentación", 55000),
    (1, "Ahorro personal", "Ahorro", 45000),
    (0, "Útiles escolares", "Educación", 35000),
    (0, "Transporte", "Transporte", 45000),
    (0, "Comidas", "Alimentación", 60000),
    (0, "Entretenimiento", "Ocio", 30000),
    (0, "Ahorro personal", "Ahorro", 40000),
]


def crear_estudiante(usuario_id: int):
    """
    Inserta el perfil de estudiante y sus datos de ejemplo.

    PARÁMETROS:
        usuario_id -> id de la cuenta demo en la tabla "usuario".

    COMPORTAMIENTO:
        - Si el estudiante ya existe, primero BORRA sus ingresos, gastos y
          presupuestos antiguos, y después los vuelve a insertar. Así el
          script se puede ejecutar muchas veces sin duplicar datos.
        - Si no existe, crea la fila en "estudiante" con el grado e
          institución de ejemplo.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:

            # 1) Buscamos si el estudiante ya existe para esta cuenta
            cur.execute("SELECT id FROM estudiante WHERE usuario_id=%s", (usuario_id,))
            row = cur.fetchone()

            if row:
                # Ya existe: guardamos su id y borramos sus datos de ejemplo
                estudiante_id = row["id"]
                for tabla in ("ingreso", "gasto", "presupuesto"):
                    cur.execute(f"DELETE FROM {tabla} WHERE estudiante_id=%s", (estudiante_id,))
            else:
                # No existe: creamos el perfil de estudiante por primera vez
                cur.execute(
                    "INSERT INTO estudiante (grado, institucion, saldo_actual, usuario_id) "
                    "VALUES (%s, %s, %s, %s)",
                    ("11°", "Institución Educativa Demo", 0.00, usuario_id),
                )
                estudiante_id = cur.lastrowid  # id que MySQL acaba de asignar

            # 2) Insertamos los ingresos de ejemplo (repartidos en 6 meses)
            for meses_antes, descripcion, monto in INGRESOS:
                cur.execute(
                    "INSERT INTO ingreso (monto, descripcion, categoria, fecha, estudiante_id) "
                    "VALUES (%s, %s, %s, CURRENT_DATE - INTERVAL %s MONTH, %s)",
                    (monto, descripcion, "Ingreso", meses_antes, estudiante_id),
                )

            # 3) Insertamos los gastos de ejemplo (cada uno con su categoría)
            for meses_antes, descripcion, categoria, monto in GASTOS:
                cur.execute(
                    "INSERT INTO gasto (monto, descripcion, categoria, fecha, estudiante_id) "
                    "VALUES (%s, %s, %s, CURRENT_DATE - INTERVAL %s MONTH, %s)",
                    (monto, descripcion, categoria, meses_antes, estudiante_id),
                )

            # 4) Creamos un presupuesto mensual de $500.000 desde hoy hasta
            #    el mismo día del próximo mes
            cur.execute(
                "INSERT INTO presupuesto (monto_limite, periodo, fecha_inicio, fecha_fin, estudiante_id) "
                "VALUES (%s, %s, CURRENT_DATE, CURRENT_DATE + INTERVAL 1 MONTH, %s)",
                (500000, "Mensual", estudiante_id),
            )

        # Una sola transacción evita dejar datos demo a medias si falla un INSERT.
        conn.commit()
    finally:
        conn.close()    # Cerramos la conexión siempre


def main():
    """Función principal: crea la cuenta demo y, si existe, le agrega datos."""
    print("Creando usuario de prueba...")

    # 1) Crea la cuenta (si ya existe, registrar_usuario avisa y no duplica)
    exito, mensaje = registrar_usuario(**DEMO)
    print(mensaje)

    # 2) Buscamos el id de la cuenta demo en la tabla "usuario"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM usuario WHERE email=%s", (DEMO["email"],))
            row = cur.fetchone()
        usuario_id = row["id"] if row else None
    finally:
        conn.close()

    # 3) Si la cuenta existe, le creamos el perfil de estudiante + datos demo
    if usuario_id:
        crear_estudiante(usuario_id)
        print("Perfil de estudiante y datos de ejemplo creados.")

    # 4) Si la cuenta se creó ahora, mostramos cómo iniciar sesión
    if exito:
        print()
        print("Ahora puedes iniciar sesión con:")
        print(f"  Correo:    {DEMO['email']}")
        print(f"  Contraseña: {DEMO['password']}")


# ---------------------------------------------------------------------------
# PUNTO DE ENTRADA: se ejecuta solo si corremos este archivo directamente
#   python -m scripts.seed_demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()