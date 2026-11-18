"""=============================================================
FinovaTech v10 - Reportes descargables (PDF y gráfico PNG)
=============================================================
La actividad "Instructivo de pruebas y reportes para el PMV"
(Guía 7) exige un reporte PDF de "Resumen mensual" y un gráfico
PNG de gastos por categoría, generados desde datos reales.

Funciones públicas:
  obtener_resumen_mensual(usuario_id, anio, mes) -> dict
  generar_pdf_resumen(usuario_id, anio, mes)     -> bytes
  generar_grafico_gastos(usuario_id, anio, mes)  -> bytes

No modifican datos: solo leen MySQL y construyen archivos en
memoria (BytesIO), por lo que las rutas HTTP no escriben en disco.
============================================================="""

import io

from datetime import date, datetime

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from fpdf import FPDF

from app.db import get_connection
from app.modelos.finanzas import MESES_LARGOS, _fmt, get_estudiante_id

TITULO_REPORTE = "Resumen mensual"
EMPRESA = "FinovaTech"

# A4 (210 mm) con márgenes de 10 mm deja 190 mm útiles para la tabla.
ANCHOS_TABLA = (20, 25, 75, 35, 35)


def _texto(valor) -> str:
    """Normaliza texto a latin-1, la codificación de las fuentes base de PDF."""
    return str(valor if valor is not None else "").encode("latin-1", "replace").decode("latin-1")


def _recortar(pdf: FPDF, texto: str, ancho: float) -> str:
    """Acorta un texto hasta que quepa en el ancho de la celda (en mm)."""
    texto = _texto(texto)
    if pdf.get_string_width(texto) <= ancho - 2:
        return texto
    while texto and pdf.get_string_width(texto + "...") > ancho - 2:
        texto = texto[:-1]
    return texto + "..."


def _periodo(anio=None, mes=None) -> tuple:
    """Devuelve (anio, mes, primer_dia, primer_dia_del_siguiente, etiqueta)."""
    hoy = date.today()
    anio = int(anio or hoy.year)
    mes = int(mes or hoy.month)
    if not 1 <= mes <= 12:
        raise ValueError("El mes debe estar entre 1 y 12.")
    inicio = date(anio, mes, 1)
    siguiente = date(anio + (mes == 12), (mes % 12) + 1, 1)
    etiqueta = f"{MESES_LARGOS[mes - 1]} {anio}"
    return anio, mes, inicio, siguiente, etiqueta


def obtener_resumen_mensual(usuario_id: int, anio=None, mes=None) -> dict:
    """Reúne los movimientos del mes y calcula ingresos, gastos y saldo.

    Los movimientos se devuelven ordenados por fecha ascendente. Si el
    usuario no tiene perfil de estudiante, el resumen queda vacío.
    """
    _, _, inicio, siguiente, etiqueta = _periodo(anio, mes)
    resumen = {
        "periodo": etiqueta,
        "generado": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "movimientos": [],
        "por_categoria": [],
        "total_ingresos": 0.0,
        "total_gastos": 0.0,
        "saldo": 0.0,
        "hay_datos": False,
    }

    estudiante_id = get_estudiante_id(usuario_id)
    if estudiante_id is None:
        return resumen

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 'Ingreso' AS tipo, descripcion, categoria, monto, fecha FROM ingreso "
                "WHERE estudiante_id=%s AND fecha>=%s AND fecha<%s "
                "UNION ALL "
                "SELECT 'Gasto' AS tipo, descripcion, categoria, monto, fecha FROM gasto "
                "WHERE estudiante_id=%s AND fecha>=%s AND fecha<%s "
                "ORDER BY fecha ASC, tipo ASC",
                (estudiante_id, inicio, siguiente, estudiante_id, inicio, siguiente),
            )
            filas = cur.fetchall()
    finally:
        conn.close()

    ingresos = 0.0
    gastos = 0.0
    categorias = {}
    for fila in filas:
        monto = float(fila["monto"])
        if fila["tipo"] == "Ingreso":
            ingresos += monto
        else:
            gastos += monto
            categorias[fila["categoria"]] = categorias.get(fila["categoria"], 0.0) + monto
        resumen["movimientos"].append({
            "tipo": fila["tipo"],
            "descripcion": fila["descripcion"],
            "categoria": fila["categoria"],
            "monto": monto,
            "monto_texto": _fmt(monto),
            "fecha": fila["fecha"].strftime("%d/%m/%Y") if fila["fecha"] else "",
        })

    resumen["total_ingresos"] = ingresos
    resumen["total_gastos"] = gastos
    resumen["saldo"] = ingresos - gastos
    resumen["hay_datos"] = bool(filas)
    resumen["por_categoria"] = [
        {"categoria": categoria, "total": total}
        for categoria, total in sorted(categorias.items(), key=lambda par: par[1], reverse=True)
    ]
    return resumen


def _encabezado_pdf(pdf: FPDF, resumen: dict):
    """Dibuja el título, la fecha de generación y el periodo del reporte."""
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, _texto(TITULO_REPORTE), new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _texto(f"{EMPRESA} - Gestion de finanzas personales"),
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 6, _texto(f"Fecha y hora de generacion: {resumen['generado']}"),
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 6, _texto(f"Periodo: {resumen['periodo']}"),
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)


def _tabla_movimientos(pdf: FPDF, resumen: dict):
    """Dibuja la tabla de movimientos ordenada y con montos formateados."""
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(22, 90, 74)
    pdf.set_text_color(255, 255, 255)
    encabezados = ("Tipo", "Fecha", "Descripcion", "Categoria", "Monto ($)")
    for encabezado, ancho in zip(encabezados, ANCHOS_TABLA):
        pdf.cell(ancho, 8, _texto(encabezado), border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    if not resumen["movimientos"]:
        pdf.cell(sum(ANCHOS_TABLA), 8, _texto("Sin movimientos registrados en el periodo"),
                 border=1, align="C", new_x="LMARGIN", new_y="NEXT")
        return

    for movimiento in resumen["movimientos"]:
        pdf.cell(ANCHOS_TABLA[0], 7, _texto(movimiento["tipo"]), border=1)
        pdf.cell(ANCHOS_TABLA[1], 7, _texto(movimiento["fecha"]), border=1, align="C")
        pdf.cell(ANCHOS_TABLA[2], 7,
                 _recortar(pdf, movimiento["descripcion"], ANCHOS_TABLA[2]), border=1)
        pdf.cell(ANCHOS_TABLA[3], 7,
                 _recortar(pdf, movimiento["categoria"], ANCHOS_TABLA[3]), border=1)
        pdf.cell(ANCHOS_TABLA[4], 7, _texto(movimiento["monto_texto"]), border=1, align="R")
        pdf.ln()


def _totales_pdf(pdf: FPDF, resumen: dict):
    """Muestra ingresos, gastos y saldo con su unidad monetaria."""
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _texto("Totales del periodo"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, _texto(f"Total ingresos ($): {_fmt(resumen['total_ingresos'])}"),
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, _texto(f"Total gastos ($): {_fmt(resumen['total_gastos'])}"),
             new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, _texto(f"Saldo ($): {_fmt(resumen['saldo'])}"),
             new_x="LMARGIN", new_y="NEXT")


def generar_pdf_resumen(usuario_id: int, anio=None, mes=None) -> bytes:
    """Construye el PDF "Resumen mensual" y devuelve sus bytes."""
    resumen = obtener_resumen_mensual(usuario_id, anio, mes)

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    # Sin compresión el contenido de texto queda legible para verificaciones.
    pdf.compress = False
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(10, 12, 10)
    pdf.add_page()
    _encabezado_pdf(pdf, resumen)
    _tabla_movimientos(pdf, resumen)
    _totales_pdf(pdf, resumen)

    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 10, _texto(f"{EMPRESA} - Reporte generado automaticamente"),
             new_x="LMARGIN", new_y="NEXT", align="C")

    return bytes(pdf.output())


def generar_grafico_gastos(usuario_id: int, anio=None, mes=None) -> bytes:
    """Genera un PNG con los gastos del mes agrupados por categoría."""
    resumen = obtener_resumen_mensual(usuario_id, anio, mes)
    categorias = [fila["categoria"] for fila in resumen["por_categoria"]]
    valores = [fila["total"] for fila in resumen["por_categoria"]]

    figura, eje = plt.subplots(figsize=(7, 4), dpi=120)
    try:
        if valores:
            colores = plt.get_cmap("tab20").colors
            barras = eje.bar(
                categorias,
                valores,
                color=[colores[i % len(colores)] for i in range(len(valores))],
            )
            eje.set_title(f"Gastos por categoria - {resumen['periodo']}")
            eje.set_ylabel("Gastos ($)")
            eje.tick_params(axis="x", rotation=35)
            for barra, valor in zip(barras, valores):
                eje.annotate(
                    _fmt(valor),
                    (barra.get_x() + barra.get_width() / 2, barra.get_height()),
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )
            eje.grid(axis="y", linestyle="--", alpha=0.4)
        else:
            eje.text(0.5, 0.5, "Sin gastos registrados en el periodo",
                     ha="center", va="center", transform=eje.transAxes, fontsize=12)
            eje.set_axis_off()
        figura.tight_layout()
        buffer = io.BytesIO()
        figura.savefig(buffer, format="png")
        return buffer.getvalue()
    finally:
        plt.close(figura)
