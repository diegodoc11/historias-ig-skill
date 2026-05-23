"""
scan_fotos.py — Cataloga las imágenes de la carpeta fotos/ en catalogo.json.

Uso: python scan_fotos.py --proj-dir /ruta/al/proyecto
"""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageOps

EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp"}


def catalogar(proj_dir: Path) -> list:
    carpeta = proj_dir / "fotos"
    fotos = []
    if not carpeta.exists():
        return fotos
    for archivo in sorted(carpeta.iterdir()):
        if archivo.suffix.lower() not in EXTENSIONES:
            continue
        try:
            im = ImageOps.exif_transpose(Image.open(archivo))
            ancho, alto = im.size
            orientacion = "vertical" if alto >= ancho else "horizontal"
        except Exception:
            ancho = alto = 0
            orientacion = "desconocida"
        fotos.append({
            "archivo": archivo.name,
            "orientacion": orientacion,
            "ancho": ancho,
            "alto": alto,
            "descripcion": "",
            "tags": [],
        })
    return fotos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proj-dir", default=".", help="Carpeta raíz del proyecto")
    args = parser.parse_args()

    proj_dir = Path(args.proj_dir).resolve()
    fotos = catalogar(proj_dir)
    (proj_dir / "catalogo.json").write_text(
        json.dumps(fotos, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"{len(fotos)} foto(s) catalogada(s) -> catalogo.json")
    for f in fotos:
        print(f"  - {f['archivo']} ({f['orientacion']}, {f['ancho']}x{f['alto']})")


if __name__ == "__main__":
    main()
