"""Genera un DOCX con diseño real (portada, indice, colores) desde el Markdown del informe.

Uso: python tools/md2docx.py <entrada.md> <salida.docx>
Soporta: encabezados #..####, listas - y 1., tablas de tuberias, bloques de codigo,
citas >, negritas **x**, codigo en linea `x`, imagenes ![alt](ruta) y reglas ---.
"""
import os
import re
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

PRIMARIO = "0F3D5C"
ACENTO = "F4A300"
TEXTO = "263238"
GRIS = "F2F5F7"
GRIS_CLARO = "FFFFFF"
CREMA = "FFF7E6"
BORDE = "D3DCE3"
FUENTE = "Arial"
MONO = "Consolas"
AUTOR = "Samuel Eduardo Bugueno Vega"
REPO = "https://github.com/samueleduardobuguenovega-lang/ProyectoFirebase"
FIREBASE = "mascotas-firestore-u3"

RE_IMAGEN = re.compile(r"^!\[(?P<alt>[^\]]*)\]\((?P<ruta>[^)]+)\)\s*$")
RE_META = re.compile(r"^\*\*(?P<clave>[^*]+):\*\*\s*(?P<valor>.+)$")


def _el(tag, **attrs):
    nodo = OxmlElement(tag)
    for clave, valor in attrs.items():
        nodo.set(qn("w:" + clave), str(valor))
    return nodo


def sombrear(par, relleno):
    """Rellena el fondo del parrafo."""
    pPr = par._p.get_or_add_pPr()
    pPr.append(_el("w:shd", val="clear", color="auto", fill=relleno))


def bordes_par(par, color=BORDE, tam=6, lados=("top", "left", "bottom", "right")):
    pPr = par._p.get_or_add_pPr()
    pBdr = _el("w:pBdr")
    for lado in lados:
        pBdr.append(_el("w:" + lado, val="single", sz=tam, space="4", color=color))
    pPr.append(pBdr)


def borde_inferior(par, color=ACENTO, tam=12):
    pPr = par._p.get_or_add_pPr()
    pBdr = _el("w:pBdr")
    pBdr.append(_el("w:bottom", val="single", sz=tam, space="2", color=color))
    pPr.append(pBdr)


def relleno_celda(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    tcPr.append(_el("w:shd", val="clear", color="auto", fill=color))


def agregar_runs(par, texto, tam=None, color=None, mono=False):
    """Interpreta **negrita** y `codigo` dentro de una linea."""
    for trozo in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", texto):
        if not trozo:
            continue
        if trozo.startswith("**") and trozo.endswith("**"):
            run = par.add_run(trozo[2:-2])
            run.bold = True
        elif trozo.startswith("`") and trozo.endswith("`"):
            run = par.add_run(trozo[1:-1])
            run.font.name = MONO
            run.font.size = Pt(9)
        else:
            run = par.add_run(trozo)
        if mono:
            run.font.name = MONO
            run.font.size = Pt(9)
        if tam and not (trozo.startswith("`") and trozo.endswith("`")):
            run.font.size = Pt(tam)
        if color:
            run.font.color.rgb = RGBColor.from_string(color)
    return par


def campo(par, instruccion):
    """Inserta un campo de Word (PAGE, NUMPAGES)."""
    fld = _el("w:fldSimple", instr=" %s " % instruccion)
    run = OxmlElement("w:r")
    run.append(OxmlElement("w:t"))
    run[-1].text = "1"
    fld.append(run)
    par._p.append(fld)


def configurar(doc, titulo_corto):
    seccion = doc.sections[0]
    seccion.page_width = Cm(21)
    seccion.page_height = Cm(29.7)
    for lado in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(seccion, lado, Cm(2.2))

    normal = doc.styles["Normal"]
    normal.font.name = FUENTE
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string(TEXTO)
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.line_spacing = 1.15

    for nivel in (1, 2, 3):
        estilo = doc.styles["Heading %d" % nivel]
        estilo.font.name = FUENTE
        estilo.font.color.rgb = RGBColor.from_string(PRIMARIO)
        estilo.font.bold = True
        estilo.paragraph_format.keep_with_next = True

    pie = seccion.footer.paragraphs[0]
    pie.text = ""
    # El estilo de pie trae tabulaciones centradas propias: se anulan y se
    # define una sola tabulacion derecha al borde del area de texto.
    pPr = pie._p.get_or_add_pPr()
    tabs = _el("w:tabs")
    for pos in (4680, 9360):
        tabs.append(_el("w:tab", val="clear", pos=pos))
    tabs.append(_el("w:tab", val="right", pos=9412))
    pPr.append(tabs)
    borde_inferior(pie, PRIMARIO, 6)
    run = pie.add_run("%s  \u00b7  %s\t" % (titulo_corto, AUTOR))
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor.from_string("78858E")
    run = pie.add_run("P\u00e1gina ")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor.from_string("78858E")
    campo(pie, "PAGE")
    run = pie.add_run(" de ")
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor.from_string("78858E")
    campo(pie, "NUMPAGES")
    for r in pie.runs:
        r.font.size = Pt(8)
        r.font.color.rgb = RGBColor.from_string("78858E")


def portada(doc, titulo, subtitulo, metadatos):
    banda = doc.add_table(rows=1, cols=1)
    banda.alignment = WD_TABLE_ALIGNMENT.CENTER
    celda = banda.rows[0].cells[0]
    relleno_celda(celda, PRIMARIO)
    celda.width = Cm(16.6)
    celda.paragraphs[0].text = ""
    par = celda.paragraphs[0]
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(26)
    par.paragraph_format.space_after = Pt(26)
    run = par.add_run(titulo)
    run.bold = True
    run.font.size = Pt(19)
    run.font.color.rgb = RGBColor.from_string("FFFFFF")
    if subtitulo:
        par2 = celda.add_paragraph()
        par2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par2.paragraph_format.space_after = Pt(6)
        run = par2.add_run(subtitulo)
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor.from_string("CFE3EE")

    doc.add_paragraph()
    if metadatos:
        tabla = doc.add_table(rows=0, cols=2)
        for clave, valor in metadatos:
            celdas = tabla.add_row().cells
            celdas[0].width = Cm(4.2)
            relleno_celda(celdas[0], GRIS)
            run = celdas[0].paragraphs[0].add_run(clave)
            run.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor.from_string(PRIMARIO)
            agregar_runs(celdas[1].paragraphs[0], valor, tam=10)

    doc.add_paragraph()
    caja = doc.add_table(rows=1, cols=1)
    celda = caja.rows[0].cells[0]
    relleno_celda(celda, CREMA)
    par = celda.paragraphs[0]
    par.text = ""
    run = par.add_run("Repositorio del proyecto")
    run.bold = True
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor.from_string(PRIMARIO)
    par2 = celda.add_paragraph()
    agregar_runs(par2, REPO, tam=10)
    par3 = celda.add_paragraph()
    agregar_runs(par3, "Proyecto de Firebase: **%s**  \u00b7  colecci\u00f3n `mascotas`" % FIREBASE, tam=10)
    doc.add_page_break()


def indice(doc, lineas):
    par = doc.add_paragraph(style="Heading 1")
    run = par.add_run("Contenido")
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor.from_string("FFFFFF")
    sombrear(par, PRIMARIO)
    par.paragraph_format.space_before = Pt(0)
    par.paragraph_format.space_after = Pt(12)

    for linea in lineas:
        if linea.startswith("### "):
            texto, nivel = linea[4:], 1
        elif linea.startswith("## "):
            texto, nivel = linea[3:], 0
        else:
            continue
        entrada = doc.add_paragraph()
        entrada.paragraph_format.left_indent = Cm(0.8 * nivel)
        entrada.paragraph_format.space_after = Pt(3)
        run = entrada.add_run(texto)
        run.font.size = Pt(10.5 if nivel == 0 else 10)
        run.bold = nivel == 0
        run.font.color.rgb = RGBColor.from_string(PRIMARIO if nivel == 0 else TEXTO)
    doc.add_page_break()


def encabezado(doc, nivel, texto):
    par = doc.add_paragraph(style="Heading %d" % min(nivel, 3))
    run = par.add_run(texto)
    if nivel == 1:
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor.from_string("FFFFFF")
        run.bold = True
        sombrear(par, PRIMARIO)
        par.paragraph_format.space_before = Pt(16)
        par.paragraph_format.space_after = Pt(8)
        par.paragraph_format.left_indent = Cm(0.25)
    elif nivel == 2:
        run.font.size = Pt(12.5)
        run.font.color.rgb = RGBColor.from_string(PRIMARIO)
        run.bold = True
        borde_inferior(par, ACENTO, 12)
        par.paragraph_format.space_before = Pt(12)
        par.paragraph_format.space_after = Pt(5)
    else:
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor.from_string(TEXTO)
        run.bold = True
        par.paragraph_format.space_before = Pt(9)
        par.paragraph_format.space_after = Pt(3)


def tabla_md(doc, filas):
    if not filas:
        return
    cabecera = [c.strip() for c in filas[0].strip("|").split("|")]
    tabla = doc.add_table(rows=1, cols=len(cabecera))
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabla.autofit = True
    for i, texto in enumerate(cabecera):
        celda = tabla.rows[0].cells[i]
        relleno_celda(celda, PRIMARIO)
        par = celda.paragraphs[0]
        agregar_runs(par, texto)
        for run in par.runs:
            run.bold = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor.from_string("FFFFFF")
    trPr = tabla.rows[0]._tr.get_or_add_trPr()
    trPr.append(_el("w:tblHeader"))

    for numero, fila in enumerate(filas[2:]):
        valores = [c.strip() for c in fila.strip("|").split("|")]
        celdas = tabla.add_row().cells
        for i, texto in enumerate(valores[: len(cabecera)]):
            celda = celdas[i]
            relleno_celda(celda, GRIS if numero % 2 else GRIS_CLARO)
            par = celda.paragraphs[0]
            par.paragraph_format.space_after = Pt(2)
            agregar_runs(par, texto, tam=9.5)
            if i == 0 and len(cabecera) <= 3:
                for run in par.runs:
                    run.bold = True
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def bloque_codigo(doc, lineas):
    par = doc.add_paragraph()
    sombrear(par, GRIS)
    bordes_par(par, BORDE, 6)
    par.paragraph_format.space_before = Pt(4)
    par.paragraph_format.space_after = Pt(8)
    par.paragraph_format.left_indent = Cm(0.3)
    par.paragraph_format.line_spacing = 1.0
    for i, linea in enumerate(lineas):
        run = par.add_run(linea)
        run.font.name = MONO
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor.from_string(TEXTO)
        if i < len(lineas) - 1:
            run.add_break()


def cita(doc, texto):
    par = doc.add_paragraph()
    sombrear(par, CREMA)
    bordes_par(par, ACENTO, 24, lados=("left",))
    bordes_par(par, BORDE, 4, lados=("top", "bottom", "right"))
    par.paragraph_format.left_indent = Cm(0.4)
    par.paragraph_format.space_before = Pt(6)
    par.paragraph_format.space_after = Pt(6)
    agregar_runs(par, texto)
    for run in par.runs:
        run.italic = True
        run.font.color.rgb = RGBColor.from_string(TEXTO)


def imagen(doc, directorio, alt, ruta):
    destino = ruta if os.path.isabs(ruta) else os.path.normpath(os.path.join(directorio, ruta))
    if not os.path.exists(destino):
        par = doc.add_paragraph()
        run = par.add_run("[imagen no encontrada: %s]" % ruta)
        run.italic = True
        run.font.color.rgb = RGBColor.from_string("B00020")
        return
    # Las capturas del telefono son verticales: se escalan por alto para que
    # quepan en la pagina; las horizontales se escalan por ancho.
    alto = None
    ancho = Cm(12)
    try:
        from PIL import Image
        with Image.open(destino) as im:
            ancho_px, alto_px = im.size
        if alto_px / float(ancho_px) > 1.2:
            ancho, alto = Cm(8), Cm(17.5)
    except Exception:
        pass
    if alto is not None:
        doc.add_picture(destino, width=ancho, height=alto)
    else:
        doc.add_picture(destino, width=ancho)
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.paragraphs[-1].paragraph_format.keep_with_next = True
    doc.paragraphs[-1].paragraph_format.space_before = Pt(6)
    if alt:
        pie = doc.add_paragraph()
        pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pie.paragraph_format.space_after = Pt(10)
        run = pie.add_run(alt)
        run.italic = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor.from_string("78858E")


def convertir(origen, destino):
    with open(origen, encoding="utf-8") as fh:
        lineas = fh.read().splitlines()

    titulo = next((l[2:].strip() for l in lineas if l.startswith("# ")), "Informe")
    corte = next((i for i, l in enumerate(lineas) if l.startswith("## ")), len(lineas))
    metadatos = []
    for linea in lineas[:corte]:
        m = RE_META.match(linea.strip())
        if m:
            metadatos.append((m.group("clave").strip(), m.group("valor").strip()))
    subtitulo = ""
    corto = re.sub(r"\s+[—-]\s+.*$", "", titulo.replace("Informe ", ""))
    corto = " ".join(corto.split()[:3])

    doc = Document()
    configurar(doc, corto)
    portada(doc, titulo.lstrip("# ").strip(), subtitulo, metadatos)
    indice(doc, lineas[corte:])

    directorio = os.path.dirname(os.path.abspath(origen))
    tabla, codigo = [], []
    en_codigo = False

    for crudo in lineas[corte:]:
        linea = crudo.rstrip()

        if linea.startswith("```"):
            if en_codigo:
                bloque_codigo(doc, codigo)
                codigo = []
            en_codigo = not en_codigo
            continue
        if en_codigo:
            codigo.append(crudo)
            continue

        if linea.startswith("|"):
            tabla.append(linea)
            continue
        if tabla:
            tabla_md(doc, tabla)
            tabla = []

        imagen_md = RE_IMAGEN.match(linea.strip())
        if imagen_md:
            imagen(doc, directorio, imagen_md.group("alt"), imagen_md.group("ruta"))
            continue

        if not linea.strip() or linea.strip() == "---":
            continue
        if linea.startswith("#"):
            nivel = len(linea) - len(linea.lstrip("#"))
            encabezado(doc, nivel - 1 if nivel > 1 else 1, linea[nivel:].strip())
        elif linea.startswith("> "):
            cita(doc, linea[2:])
        elif linea.startswith("- "):
            agregar_runs(doc.add_paragraph(style="List Bullet"), linea[2:])
        elif re.match(r"^\d+\. ", linea):
            agregar_runs(doc.add_paragraph(style="List Number"), re.sub(r"^\d+\. ", "", linea))
        else:
            agregar_runs(doc.add_paragraph(), linea)

    if tabla:
        tabla_md(doc, tabla)

    doc.save(destino)
    print("OK ->", destino)


if __name__ == "__main__":
    convertir(sys.argv[1], sys.argv[2])
