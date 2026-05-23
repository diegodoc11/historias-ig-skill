"""
utils.py — Utilidades de renderizado para historias y carruseles de Instagram.

Lienzo por defecto: 1080 x 1920 (9:16). Tipografía: Space Grotesk.
Implementación propia del pipeline de imagen (fondo, overlays, texto, guardado).
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H = 1080, 1920


# ── Configuración y color ────────────────────────────────────────────────────

def load_config(proj_dir) -> dict:
    cfg = Path(proj_dir) / "config.json"
    if not cfg.exists():
        raise FileNotFoundError(
            "Falta config.json. Ejecuta /historias-ig para configurar tu marca.")
    return json.loads(cfg.read_text(encoding="utf-8"))


def _hex_to_rgb(value: str) -> tuple:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def colors_from_config(cfg: dict) -> dict:
    paleta = cfg.get("colores", {}) or {}
    return {
        "BG": _hex_to_rgb(paleta.get("fondo", "#08080F")),
        "PRIMARY": _hex_to_rgb(paleta.get("primario", "#00E5FF")),
        "WHITE": (255, 255, 255),
        "DIM": (180, 185, 195),
        "YELLOW": (255, 230, 50),
    }


# ── Tipografía y lienzo ──────────────────────────────────────────────────────

def font(proj_dir, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    nombre = "SpaceGrotesk-Bold.ttf" if bold else "SpaceGrotesk-Variable.ttf"
    try:
        return ImageFont.truetype(str(Path(proj_dir) / "fonts" / nombre), size)
    except Exception:
        return ImageFont.load_default()


def new_canvas(colors: dict) -> Image.Image:
    return Image.new("RGBA", (W, H), (*colors["BG"], 255))


# ── Fondos ───────────────────────────────────────────────────────────────────

def load_bg(path, darken: float = 0.55, blur: int = 0) -> Image.Image:
    """Abre una imagen, respeta su orientación EXIF, la recorta tipo 'cover' al
    lienzo y le aplica un oscurecido uniforme."""
    src = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
    factor = max(W / src.width, H / src.height)
    src = src.resize((round(src.width * factor), round(src.height * factor)), Image.LANCZOS)
    x = (src.width - W) // 2
    y = (src.height - H) // 2
    bg = src.crop((x, y, x + W, y + H))
    if blur:
        bg = bg.filter(ImageFilter.GaussianBlur(blur))
    if darken > 0:
        bg.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * darken))))
    return bg


def gradient_overlay(img: Image.Image, direction: str = "bottom", strength: float = 0.80):
    """Aplica un degradado negro (para legibilidad del texto) en una dirección."""
    column = Image.new("L", (1, H), 0)
    px = column.load()
    for y in range(H):
        if direction == "top":
            t = 1 - y / H
        elif direction == "center":
            t = abs(y / H - 0.5) * 2
        else:  # bottom
            t = y / H
        px[0, y] = int(255 * strength * (t ** 1.5))
    alpha = column.resize((W, H))
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    veil.putalpha(alpha)
    img.alpha_composite(veil)


# ── Texto ────────────────────────────────────────────────────────────────────

def _wrap(draw, text, fnt, max_w):
    palabras = str(text).split()
    lineas, actual = [], []
    for p in palabras:
        prueba = " ".join(actual + [p])
        if actual and draw.textlength(prueba, font=fnt) > max_w:
            lineas.append(" ".join(actual))
            actual = [p]
        else:
            actual.append(p)
    if actual:
        lineas.append(" ".join(actual))
    return lineas


def draw_text(draw, text, y, fnt, color=(255, 255, 255), max_w=940,
              line_gap=14, shadow=True, stroke=0):
    """Texto centrado horizontalmente con ajuste de línea. Devuelve la y final."""
    alto_linea = fnt.size + line_gap
    for linea in _wrap(draw, text, fnt, max_w):
        ancho = draw.textlength(linea, font=fnt)
        x = (W - ancho) // 2
        if shadow:
            draw.text((x + 3, y + 3), linea, font=fnt, fill=(0, 0, 0, 160))
        draw.text((x, y), linea, font=fnt, fill=color,
                  stroke_width=stroke, stroke_fill=color if stroke else None)
        y += alto_linea
    return y


def draw_pill(draw, text, y, fnt, bg_color, text_color=(8, 8, 16)):
    """Etiqueta tipo 'píldora' centrada."""
    ancho_txt = draw.textlength(text, font=fnt)
    pw, ph = int(ancho_txt) + 56, fnt.size + 30
    px = (W - pw) // 2
    draw.rounded_rectangle([px, y, px + pw, y + ph], radius=ph // 2, fill=(*bg_color, 235))
    draw.text((px + 28, y + 15), text, font=fnt, fill=text_color)
    return y + ph


def progress_bar(draw, current, total, primary):
    """Barra segmentada de progreso en la parte superior."""
    margen, sep = 24, 12
    ancho_seg = (W - 2 * margen - sep * (total - 1)) // max(total, 1)
    x = margen
    for i in range(total):
        color = (*primary, 255) if i < current else (255, 255, 255, 90)
        draw.rounded_rectangle([x, 26, x + ancho_seg, 32], radius=3, fill=color)
        x += ancho_seg + sep


# ── Guardado ─────────────────────────────────────────────────────────────────

def save(img: Image.Image, output_dir, name: str) -> Path:
    """Aplana sobre negro y guarda como PNG optimizado."""
    plano = Image.new("RGB", (W, H), (0, 0, 0))
    mask = img.split()[3] if img.mode == "RGBA" else None
    plano.paste(img.convert("RGB"), mask=mask)
    destino = Path(output_dir) / name
    plano.save(destino, "PNG", optimize=True)
    print(f"  generado: {name}")
    return destino
