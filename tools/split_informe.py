"""Parte el informe de la Unidad 3 en un documento por actividad.

Uso: python tools/split_informe.py
Lee docs/informe_unidad3_firebase.md y genera:
  docs/informe_3_1.md  (investigacion, modelo de datos, cierre 3.1 y anexo)
  docs/informe_3_2.md  (procedimiento, verificacion, prueba en el telefono y cierre 3.2)
"""
import os

BASE = os.path.join("docs", "informe_unidad3_firebase.md")
TITULO_31 = "# Informe Actividad 3.1 — Manejo de base de datos externa (Firebase)"
TITULO_32 = "# Informe Actividad 3.2 — Desarrollo de funcionalidades avanzadas con Firebase"


def leer_lineas():
    with open(BASE, encoding="utf-8") as fh:
        return fh.read().splitlines()


def indice(lineas, prefijo, desde=0):
    for i in range(desde, len(lineas)):
        if lineas[i].startswith(prefijo):
            return i
    raise SystemExit("No se encontro la seccion: " + prefijo)


def escribir(destino, titulo, lineas):
    # La primera linea del informe base es el titulo; se reemplaza.
    cuerpo = [titulo] + lineas[1:]
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(cuerpo) + "\n")
    print("OK ->", destino)


def main():
    lineas = leer_lineas()
    cabecera = lineas[: indice(lineas, "## 1.")]
    inicio_31 = indice(lineas, "## 1.")
    inicio_32 = indice(lineas, "## 2. Actividad 3.2")
    inicio_anexo = indice(lineas, "## Anexo")

    # 3.1: investigacion, modelo de datos, cierre y anexo del material.
    parte_31 = lineas[inicio_31:inicio_32] + lineas[inicio_anexo:]
    # 3.2: procedimiento, verificacion y prueba final.
    parte_32 = lineas[inicio_32:inicio_anexo]

    escribir(os.path.join("docs", "informe_3_1.md"), TITULO_31, cabecera + parte_31)
    escribir(os.path.join("docs", "informe_3_2.md"), TITULO_32, cabecera + parte_32)


if __name__ == "__main__":
    main()
