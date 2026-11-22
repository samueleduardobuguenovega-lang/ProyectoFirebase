"""Convierte el informe en Markdown a DOCX para subir a Moodle.

Uso: python tools/md2docx.py docs/informe_unidad3_firebase.md docs/Informe_Unidad3_Firebase.docx
Soporta: encabezados (#..####), listas con -, tablas de tuberias, bloques de codigo,
citas (>), negritas **x**, codigo en linea `x` y reglas horizontales.
"""
import re
import sys

from docx import Document
from docx.shared import Pt, RGBColor


def add_runs(par, text, mono=False):
    """Agrega texto interpretando **negrita** y `codigo`."""
    for piece in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**"):
            run = par.add_run(piece[2:-2])
            run.bold = True
        elif piece.startswith("`") and piece.endswith("`"):
            run = par.add_run(piece[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)
        else:
            run = par.add_run(piece)
        if mono:
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)


def flush_table(doc, rows):
    if not rows:
        return
    celdas = [c.strip() for c in rows[0].strip("|").split("|")]
    tabla = doc.add_table(rows=1, cols=len(celdas))
    tabla.style = "Table Grid"
    for i, texto in enumerate(celdas):
        par = tabla.rows[0].cells[i].paragraphs[0]
        add_runs(par, texto)
        for run in par.runs:
            run.bold = True
    for fila in rows[2:]:
        valores = [c.strip() for c in fila.strip("|").split("|")]
        cells = tabla.add_row().cells
        for i, texto in enumerate(valores[: len(celdas)]):
            add_runs(cells[i].paragraphs[0], texto)
    doc.add_paragraph()


def convertir(origen, destino):
    doc = Document()
    estilo = doc.styles["Normal"]
    estilo.font.name = "Calibri"
    estilo.font.size = Pt(11)

    with open(origen, encoding="utf-8") as fh:
        lineas = fh.read().splitlines()

    tabla = []
    codigo = []
    en_codigo = False

    for linea in lineas:
        crudo = linea.rstrip()

        if crudo.startswith("```"):
            if en_codigo:
                par = doc.add_paragraph()
                add_runs(par, "\n".join(codigo), mono=True)
                codigo = []
            en_codigo = not en_codigo
            continue
        if en_codigo:
            codigo.append(linea)
            continue

        if crudo.startswith("|"):
            tabla.append(crudo)
            continue
        if tabla:
            flush_table(doc, tabla)
            tabla = []

        if not crudo.strip() or crudo.strip() == "---":
            continue

        if crudo.startswith("#"):
            nivel = len(crudo) - len(crudo.lstrip("#"))
            doc.add_heading(crudo[nivel:].strip(), level=min(nivel, 4))
        elif crudo.startswith("- "):
            par = doc.add_paragraph(style="List Bullet")
            add_runs(par, crudo[2:])
        elif crudo.startswith("> "):
            par = doc.add_paragraph()
            run = par.add_run(crudo[2:])
            run.italic = True
            run.font.color.rgb = RGBColor(0x60, 0x60, 0x60)
        elif re.match(r"^\d+\. ", crudo):
            par = doc.add_paragraph(style="List Number")
            add_runs(par, re.sub(r"^\d+\. ", "", crudo))
        else:
            add_runs(doc.add_paragraph(), crudo)

    if tabla:
        flush_table(doc, tabla)

    doc.save(destino)
    print("OK ->", destino)


if __name__ == "__main__":
    convertir(sys.argv[1], sys.argv[2])
