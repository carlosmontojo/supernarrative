"""Descarga legislación consolidada del BOE como texto plano para el corpus.

Usa la API de datos abiertos del BOE (legislación consolidada). Para cada
bloque de la norma toma la versión vigente más reciente, extrae el texto y lo
guarda en corpus/boe/<id>.txt listo para prepare.py.

Los textos legales españoles no tienen derechos de autor (art. 13 LPI):
corpus limpio y para siempre.

Uso:
    python boe.py BOE-A-2006-20764                  # Ley del IRPF
    python boe.py BOE-A-1992-28740 BOE-A-2014-12328 # IVA, Ley del IS
"""
import argparse
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

API = "https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/{id}/texto"


def fetch(boe_id: str) -> bytes:
    req = urllib.request.Request(
        API.format(id=boe_id), headers={"Accept": "application/xml"}
    )
    with urllib.request.urlopen(req) as r:
        return r.read()


def extract_text(xml_bytes: bytes) -> str:
    root = ET.fromstring(xml_bytes)
    parts = []
    for bloque in root.iter("bloque"):
        versiones = bloque.findall("version")
        if not versiones:
            continue
        # Cada bloque puede tener varias redacciones históricas: nos quedamos
        # con la vigente más reciente.
        vigente = max(versiones, key=lambda v: v.get("fecha_vigencia") or "")
        text = " ".join("".join(vigente.itertext()).split())
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+", help="ids del BOE, p. ej. BOE-A-2006-20764")
    ap.add_argument("--out", default="corpus/boe")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for boe_id in args.ids:
        if not re.fullmatch(r"BOE-A-\d{4}-\d+", boe_id):
            raise SystemExit(f"id no válido: {boe_id} (formato BOE-A-AAAA-NNNNN)")
        print(f"Descargando {boe_id} ...")
        text = extract_text(fetch(boe_id))
        path = out_dir / f"{boe_id}.txt"
        path.write_text(text, encoding="utf-8")
        print(f"  {path}: {len(text):,} caracteres")


if __name__ == "__main__":
    main()
