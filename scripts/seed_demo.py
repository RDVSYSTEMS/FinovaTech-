"""=============================================================================
FinovaTech v10 - Datos de prueba (demo)
===============================================================================
Crea una cuenta demo con informacion suficiente para la sustentacion:

  1. Cuenta:  adminr123@gmail.com / 123456789 (rol administrador)
  2. Perfil de estudiante con grado e institucion.
  3. Movimientos de los ultimos 6 meses en 12 categorias distintas.
  4. Presupuesto del mes vigente disenado para disparar avisos variados.
  5. El mes actual queda en negativo, supera el presupuesto y tiene un gasto
     elevado, de modo que /notificacion muestre los seis avisos posibles.
  6. Cuenta de padre vinculada al estudiante demo para mostrar /supervision.

El script es REPETIBLE: al ejecutarlo de nuevo borra los movimientos y el
presupuesto del estudiante demo y los vuelve a crear (no duplica datos).

EJECUCION (desde la raiz del proyecto):
    python -m scripts.seed_demo
============================================================================="""

import calendar
from datetime import date

from app.db import get_connection
from app.modelos.usuarios import registrar_usuario

DEMO = {
    "nombre": "Administrador Demo",
    "email": "adminr123@gmail.com",
    "username": "adminrdv",
    "password": "123456789",
    "rol": "administrador",
}

PADRE_DEMO = {
    "nombre": "Padre Demo",
    "email": "padredemo@gmail.com",
    "username": "padredemo",
    "password": "123456789",
    "rol": "padre",
}

# (meses_antes, dia_del_mes, descripcion, monto)
INGRESOS = [
    (5, 5, "Mesada", 230000),
    (5, 16, "Premio académico", 35000),
    (4, 4, "Mesada", 240000),
    (4, 18, "Trabajo fin de semana", 50000),
    (3, 3, "Mesada", 250000),
    (3, 12, "Premio académico", 40000),
    (3, 22, "Venta de libros", 30000),
    (2, 5, "Mesada", 260000),
    (2, 16, "Beca de transporte", 45000),
    (1, 2, "Mesada", 270000),
    (1, 10, "Trabajo fin de semana", 60000),
    (1, 20, "Premio académico", 40000),
    (0, 1, "Mesada", 280000),
    (0, 2, "Premio académico", 40000),
    (0, 3, "Trabajo fin de semana", 120000),
    (5, 11, "Ayudancia en laboratorio", 45000),
    (5, 24, "Venta de artesanías", 20000),
    (4, 9, "Reembolso de transporte", 18000),
    (4, 23, "Venta de apuntes", 25000),
    (3, 8, "Ayudancia en laboratorio", 50000),
    (3, 27, "Venta de libros", 22000),
    (2, 7, "Beca de alimentación", 60000),
    (2, 21, "Venta de artesanías", 28000),
    (1, 6, "Reembolso de transporte", 20000),
    (1, 24, "Trabajo fin de semana", 55000),
    (0, 12, "Beca de alimentación", 65000),
    (0, 18, "Reembolso de transporte", 15000),
]

# (meses_antes, dia_del_mes, descripcion, categoria, monto)
GASTOS = [
    (5, 8, "Útiles escolares", "Educación", 30000),
    (5, 14, "Transporte", "Transporte", 35000),
    (5, 19, "Comidas", "Alimentación", 40000),
    (5, 25, "Cine", "Ocio", 25000),
    (5, 27, "Aseo del hogar", "Hogar", 20000),
    (4, 6, "Comidas", "Alimentación", 45000),
    (4, 11, "Transporte", "Transporte", 40000),
    (4, 15, "Farmacia", "Salud", 18000),
    (4, 21, "Accesorios tecnológicos", "Tecnología", 60000),
    (4, 26, "Ropa", "Ropa", 25000),
    (3, 5, "Transporte", "Transporte", 45000),
    (3, 9, "Comidas", "Alimentación", 50000),
    (3, 14, "Ahorro personal", "Ahorro", 30000),
    (3, 20, "Útiles escolares", "Educación", 25000),
    (3, 26, "Alimento para mascota", "Mascotas", 12000),
    (2, 4, "Comidas", "Alimentación", 55000),
    (2, 10, "Entretenimiento", "Ocio", 35000),
    (2, 16, "Transporte", "Transporte", 42000),
    (2, 22, "Regalo cumpleaños", "Regalos", 18000),
    (2, 27, "Suscripción streaming", "Suscripciones", 12000),
    (1, 3, "Comidas", "Alimentación", 60000),
    (1, 8, "Transporte", "Transporte", 45000),
    (1, 13, "Ahorro personal", "Ahorro", 50000),
    (1, 19, "Farmacia", "Salud", 22000),
    (1, 25, "Aseo del hogar", "Hogar", 30000),
    (0, 1, "Mercado semanal", "Alimentación", 70000),
    (0, 1, "Pasajes del mes", "Transporte", 40000),
    (0, 2, "Útiles escolares", "Educación", 30000),
    (0, 2, "Comidas fuera de casa", "Alimentación", 50000),
    (0, 3, "Cine con amigos", "Ocio", 25000),
    (0, 3, "Farmacia", "Salud", 20000),
    (0, 4, "Aseo del hogar", "Hogar", 35000),
    (0, 4, "Zapatos", "Ropa", 30000),
    (0, 5, "Suscripción streaming", "Suscripciones", 15000),
    (0, 5, "Ahorro personal", "Ahorro", 25000),
    (0, 5, "Alimento para mascota", "Mascotas", 15000),
    (0, 6, "Regalo para mamá", "Regalos", 20000),
    (0, 6, "Audífonos inalámbricos", "Tecnología", 280000),
    (0, 6, "Comida con amigos", "Alimentación", 30000),
    (0, 6, "Pasajes adicionales", "Transporte", 15000),
    (5, 3, "Recarga de transporte", "Transporte", 12000),
    (5, 10, "Almuerzo en cafetería", "Alimentación", 18000),
    (5, 13, "Materiales de taller", "Educación", 22000),
    (5, 21, "Pago de internet", "Hogar", 25000),
    (5, 28, "Suscripción de música", "Suscripciones", 9000),
    (4, 3, "Copias e impresiones", "Educación", 8000),
    (4, 12, "Consulta médica", "Salud", 24000),
    (4, 17, "Libro de texto", "Educación", 35000),
    (4, 24, "Mantenimiento de bicicleta", "Transporte", 16000),
    (3, 4, "Abono a celular", "Tecnología", 20000),
    (3, 11, "Almuerzo en cafetería", "Alimentación", 19000),
    (3, 18, "Entrada al museo", "Ocio", 12000),
    (3, 25, "Uniforme escolar", "Ropa", 42000),
    (2, 3, "Café de la semana", "Alimentación", 7000),
    (2, 9, "Cuota de proyecto", "Educación", 30000),
    (2, 14, "Seguro escolar", "Salud", 26000),
    (2, 20, "Deporte", "Ocio", 15000),
    (2, 25, "Donación", "Regalos", 10000),
    (1, 4, "Recarga de transporte", "Transporte", 14000),
    (1, 11, "Papelería", "Educación", 11000),
    (1, 17, "Almuerzo en cafetería", "Alimentación", 21000),
    (1, 23, "Paseo familiar", "Ocio", 28000),
    (0, 8, "Papelería", "Educación", 12000),
    (0, 10, "Abono a celular", "Tecnología", 18000),
    (0, 14, "Café de la semana", "Alimentación", 8000),
]

MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

PRESUPUESTO_MENSUAL = 600000


def _fecha(meses_antes: int, dia: int) -> date:
    """Devuelve una fecha real dentro del mes indicado, sin fechas futuras."""
    hoy = date.today()
    indice = (hoy.year * 12 + hoy.month - 1) - meses_antes
    anio, mes = divmod(indice, 12)
    mes += 1
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    dia = min(dia, ultimo_dia)
    if meses_antes == 0:
        dia = min(dia, hoy.day)
    return date(anio, mes, dia)


def crear_estudiante(usuario_id: int):
    """Crea o reinicia el perfil de estudiante con sus datos demo."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM estudiante WHERE usuario_id=%s", (usuario_id,))
            fila = cur.fetchone()

            if fila:
                estudiante_id = fila["id"]
                for tabla in ("ingreso", "gasto", "presupuesto"):
                    cur.execute(
                        f"DELETE FROM {tabla} WHERE estudiante_id=%s",
                        (estudiante_id,),
                    )
            else:
                cur.execute(
                    "INSERT INTO estudiante (grado, institucion, saldo_actual, usuario_id) "
                    "VALUES (%s, %s, %s, %s)",
                    ("11°", "Institución Educativa Demo", 0.00, usuario_id),
                )
                estudiante_id = cur.lastrowid

            for meses_antes, dia, descripcion, monto in INGRESOS:
                cur.execute(
                    "INSERT INTO ingreso (monto, descripcion, categoria, fecha, estudiante_id) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (monto, descripcion, "Ingreso", _fecha(meses_antes, dia), estudiante_id),
                )

            for meses_antes, dia, descripcion, categoria, monto in GASTOS:
                cur.execute(
                    "INSERT INTO gasto (monto, descripcion, categoria, fecha, estudiante_id) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (monto, descripcion, categoria, _fecha(meses_antes, dia), estudiante_id),
                )

            inicio = date.today().replace(day=1)
            if inicio.month == 12:
                siguiente = date(inicio.year + 1, 1, 1)
            else:
                siguiente = date(inicio.year, inicio.month + 1, 1)
            fin = date.fromordinal(siguiente.toordinal() - 1)

            cur.execute(
                "INSERT INTO presupuesto (monto_limite, periodo, fecha_inicio, fecha_fin, estudiante_id) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    PRESUPUESTO_MENSUAL,
                    f"{MESES_ES[inicio.month - 1]} {inicio.year}",
                    inicio,
                    fin,
                    estudiante_id,
                ),
            )
        conn.commit()
    finally:
        conn.close()


def crear_padre_vinculado(estudiante_usuario_id: int):
    """Crea la cuenta de padre demo y la vincula al estudiante demo."""
    registrar_usuario(**PADRE_DEMO)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM usuario WHERE email=%s", (PADRE_DEMO["email"],))
            fila = cur.fetchone()
            if not fila:
                return None
            padre_id = fila["id"]
            cur.execute(
                "INSERT IGNORE INTO padre_estudiante "
                "(padre_id, estudiante_usuario_id) VALUES (%s, %s)",
                (padre_id, estudiante_usuario_id),
            )
        conn.commit()
        return padre_id
    finally:
        conn.close()


def main():
    """Crea la cuenta demo y reemplaza sus datos de ejemplo."""
    print("Creando usuario de prueba...")
    _, mensaje = registrar_usuario(**DEMO)
    print(mensaje)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM usuario WHERE email=%s", (DEMO["email"],))
            fila = cur.fetchone()
        usuario_id = fila["id"] if fila else None
    finally:
        conn.close()

    if usuario_id:
        crear_estudiante(usuario_id)
        padre_id = crear_padre_vinculado(usuario_id)
        print(f"Datos demo cargados: {len(INGRESOS)} ingresos y {len(GASTOS)} gastos.")
        if padre_id:
            print("Cuenta de padre vinculada al estudiante demo.")

    print()
    print("Cuentas de demostracion:")
    print(f"  Administrador/estudiante -> {DEMO['email']} / {DEMO['password']}")
    print(f"  Padre vinculado          -> {PADRE_DEMO['email']} / {PADRE_DEMO['password']}")


if __name__ == "__main__":
    main()
