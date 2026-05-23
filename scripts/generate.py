#!/usr/bin/env python3
"""
generate.py — Genera las historias de Instagram a partir de un plan JSON.

Uso:
  python3 scripts/generate.py --plan plan.json [--proj-dir /ruta/proyecto]

El plan.json tiene esta estructura:
{
  "slides": [
    {
      "numero": 1,
      "tipo": "hook",            // hook | problema | revelacion | beneficios | prueba | cta
      "titulo": "Texto grande",
      "subtitulo": "Texto secundario",
      "texto_extra": "Texto pequeño opcional",
      "foto": "nombre_foto.jpg", // null para fondo sólido o AI
      "fondo_ia": {              // null si no se usa Kie AI
        "prompt": "descripción del fondo a generar"
      },
      "palabras_clave": ["palabra1", "palabra2"], // se resaltan en color primario
      "cta_palabra": "KEYWORD"  // solo en slide tipo cta
    }
  ]
}
"""

import json
import os
import sys
import time
import threading
import urllib.request
from datetime import datetime
from pathlib import Path

# Asegurar imports del proyecto
PROJ_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJ_DIR / "scripts"))

from utils import (
    W, H, load_config, colors_from_config, font as _font,
    new_canvas, load_bg, gradient_overlay, draw_text,
    draw_pill, progress_bar, save,
)
from PIL import Image, ImageDraw


def _load_dotenv(proj_dir: Path):
    """Carga variables desde un archivo .env (sin dependencias externas)."""
    p = proj_dir / ".env"
    if not p.exists():
        return
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass


def font(proj_dir: Path, size: int, bold: bool = False):
    return _font(proj_dir, size, bold)


# ── Kie AI ─────────────────────────────────────────────────────────────────────

def kie_generate(prompt: str, api_key: str) -> str | None:
    """Genera imagen con Kie AI y retorna la URL del resultado."""
    payload = json.dumps({
        "model": "google/nano-banana",
        "input": {
            "prompt": prompt + ", professional quality, no text",
            "aspect_ratio": "9:16",
            "resolution": "1K",
            "output_format": "png",
        },
    }).encode()

    req = urllib.request.Request(
        "https://api.kie.ai/api/v1/jobs/createTask",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
        data = resp.get("data") or {}
        task_id = data.get("taskId")
        if not task_id:
            print(f"  ⚠️  Kie AI: {resp.get('msg', 'sin task_id')}")
            return None
    except Exception as e:
        print(f"  ⚠️  Kie AI error al crear tarea: {e}")
        return None

    # Polling
    for _ in range(60):
        time.sleep(3)
        try:
            poll = urllib.request.Request(
                f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            data = json.loads(urllib.request.urlopen(poll, timeout=15).read())
            inner = data.get("data") or {}
            state = inner.get("state")
            if state == "success":
                result_json = inner.get("resultJson", "{}")
                urls = json.loads(result_json).get("resultUrls", [])
                return urls[0] if urls else None
            if state in ("failed", "error"):
                print(f"  ⚠️  Kie AI tarea fallida: {inner.get('failMsg')}")
                return None
        except Exception as e:
            print(f"  ⚠️  Kie AI poll error: {e}")
    return None


def download_image(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://kie.ai/"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            dest.write_bytes(r.read())
        return True
    except Exception as e:
        print(f"  ⚠️  Error descargando imagen: {e}")
        return False


# ── Renderizado de slides ──────────────────────────────────────────────────────

def _wrap_lines(draw, text, fnt, max_w):
    words = str(text).split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        if draw.textbbox((0, 0), test, font=fnt)[2] > max_w and cur:
            lines.append(" ".join(cur)); cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines


def draw_fitted_block(draw, proj_dir, blocks, y_top, y_bottom, max_w=950, anchor="center"):
    """Dibuja varios bloques de texto centrados, escalando la fuente para que
    todo quepa dentro de [y_top, y_bottom]. blocks: lista de dicts con
    {text, size, bold, color, stroke, gap}."""
    blocks = [b for b in blocks if b.get("text")]
    scale = 1.0
    rendered, total = [], 0
    for _ in range(16):
        rendered, total = [], 0
        for b in blocks:
            s = max(22, int(b["size"] * scale))
            fnt = font(proj_dir, s, bold=b.get("bold", False))
            lines = _wrap_lines(draw, b["text"], fnt, max_w)
            lh = s + max(6, int(14 * scale))
            block_h = lh * len(lines)
            rendered.append((b, fnt, lines, lh))
            total += block_h + int(b.get("gap", 26) * scale)
        if total <= (y_bottom - y_top) or scale <= 0.5:
            break
        scale *= 0.92
    y = y_top + max(0, ((y_bottom - y_top) - total) // 2) if anchor == "center" else y_top
    for b, fnt, lines, lh in rendered:
        stroke = b.get("stroke", 0)
        for line in lines:
            bb = draw.textbbox((0, 0), line, font=fnt)
            x = (W - (bb[2] - bb[0])) // 2
            draw.text((x + 3, y + 3), line, font=fnt, fill=(0, 0, 0, 170))
            draw.text((x, y), line, font=fnt, fill=b["color"],
                      stroke_width=stroke, stroke_fill=b["color"] if stroke else None)
            y += lh
        y += int(b.get("gap", 26) * scale)
    return y


def pick_text_band(img, pos="auto", has_foto=False):
    """Devuelve (y_top, y_bottom) donde colocar el texto.
    pos: 'top' | 'center' | 'bottom' | 'auto'. En 'auto' con foto, elige entre
    la banda superior y la inferior la MÁS OSCURA (mejor contraste y suele
    evitar la cara, que casi siempre va al centro)."""
    bands = {"top": (250, 980), "center": (560, 1520), "bottom": (1060, 1830)}
    if pos in bands:
        return bands[pos]
    if not has_foto:
        return bands["bottom"]
    from PIL import ImageStat

    def lum(y0, y1):
        return ImageStat.Stat(img.crop((0, y0, W, y1)).convert("L")).mean[0]

    return bands["top"] if lum(250, 980) <= lum(1060, 1830) else bands["bottom"]


def draw_badges(img, draw, proj_dir, names, y=150):
    """Fila centrada de 'chips' de marca. Usa logos/<slug>.png si existe;
    si no, muestra el nombre en un chip blanco."""
    if not names:
        return
    fnt = font(proj_dir, 30, bold=True)
    h, gap, pad = 66, 18, 26
    specs = []
    for name in names:
        slug = "".join(c for c in name.lower() if c.isalnum())
        logo = proj_dir / "logos" / f"{slug}.png"
        if logo.exists() and logo.stat().st_size > 1000:
            specs.append(("img", logo, name, int(h * 1.9)))
        else:
            bb = draw.textbbox((0, 0), name, font=fnt)
            specs.append(("txt", None, name, (bb[2] - bb[0]) + pad * 2))
    total_w = sum(w for *_, w in specs) + gap * (len(specs) - 1)
    x = (W - total_w) // 2
    for kind, path, name, w in specs:
        draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=(255, 255, 255, 240))
        if kind == "txt":
            bb = draw.textbbox((0, 0), name, font=fnt)
            draw.text((x + (w - (bb[2] - bb[0])) // 2, y + (h - (bb[3] - bb[1])) // 2 - bb[1]),
                      name, font=fnt, fill=(12, 12, 16))
        else:
            try:
                lg = Image.open(path).convert("RGBA")
                lh = h - 22
                lw = int(lg.width * (lh / lg.height))
                if lw > w - 20:
                    lw, lh = w - 20, int(lg.height * ((w - 20) / lg.width))
                lg = lg.resize((lw, lh), Image.LANCZOS)
                img.alpha_composite(lg, (x + (w - lw) // 2, y + (h - lh) // 2))
            except Exception:
                pass
        x += w + gap


def render_slide(slide: dict, idx: int, total: int,
                 proj_dir: Path, cfg: dict, colors: dict,
                 kie_cache: dict, kie_key: str | None,
                 output_dir: Path) -> Path:

    tipo = slide.get("tipo", "hook")
    foto = slide.get("foto")
    fondo_ia = slide.get("fondo_ia")
    keywords = slide.get("palabras_clave", [])

    PRIMARY = colors["PRIMARY"]
    WHITE = colors["WHITE"]
    DIM = colors["DIM"]
    YELLOW = colors["YELLOW"]

    # ── Fondo ──────────────────────────────────────────────────────────────────
    if foto:
        foto_path = proj_dir / "fotos" / foto
        if foto_path.exists():
            img = load_bg(foto_path, darken=0.55)
            gradient_overlay(img, "bottom", 0.70)
        else:
            print(f"  ⚠️  Foto no encontrada: {foto}, usando fondo sólido")
            img = new_canvas(colors)
    elif fondo_ia and kie_key:
        cache_key = fondo_ia.get("prompt", "")
        if cache_key in kie_cache:
            img = load_bg(kie_cache[cache_key], darken=0.50)
            gradient_overlay(img, "bottom", 0.65)
        else:
            img = new_canvas(colors)
    else:
        img = new_canvas(colors)

    draw = ImageDraw.Draw(img)

    # ── Barra de progreso ──────────────────────────────────────────────────────
    progress_bar(draw, idx, total, PRIMARY)

    # ── Logos / chips de marca ───────────────────────────────────────────────────
    draw_badges(img, draw, proj_dir, slide.get("logos", []))

    # ── Contenido según tipo ───────────────────────────────────────────────────
    titulo = slide.get("titulo", "")
    subtitulo = slide.get("subtitulo", "")
    texto_extra = slide.get("texto_extra", "")

    if tipo == "hook":
        # Etiqueta en la parte superior
        draw_pill(draw, slide.get("etiqueta") or cfg.get("etiqueta_hook", "NUEVA HISTORIA"), 120,
                  font(proj_dir, 34), PRIMARY)
        # Título + subtítulo + extra, autoajustados a la banda más despejada
        y_top, y_bottom = pick_text_band(img, slide.get("texto_pos", "auto"), bool(foto))
        draw_fitted_block(draw, proj_dir, [
            {"text": titulo,    "size": 70, "bold": True,  "color": WHITE,   "stroke": 1, "gap": 20},
            {"text": subtitulo, "size": 50, "bold": False, "color": PRIMARY, "stroke": 1, "gap": 16},
            {"text": texto_extra, "size": 40, "bold": False, "color": DIM,   "gap": 0},
        ], y_top=y_top, y_bottom=y_bottom)

    elif tipo == "cta":
        cta_palabra = slide.get("cta_palabra", "PALABRA")
        cta_verbo = slide.get("cta_verbo") or (cfg.get("cta_formato") or "Responde").split()[0]
        nombre_marca = cfg.get("instagram_user") or cfg.get("nombre_marca", "@tumarca")
        # Pregunta (título) en la zona superior-media, autoajustada
        y = draw_fitted_block(draw, proj_dir, [
            {"text": titulo, "size": 64, "bold": True, "color": WHITE, "stroke": 1, "gap": 0},
        ], y_top=440, y_bottom=740, anchor="top")
        y += 30
        draw_text(draw, cta_verbo, y, font(proj_dir, 60), DIM)
        y += 92
        box_w, box_h = 580, 120
        bx = (W - box_w) // 2
        draw.rounded_rectangle([bx, y, bx + box_w, y + box_h], radius=24,
                               fill=(*YELLOW, 40), outline=YELLOW, width=3)
        kw_f = font(proj_dir, 62, bold=True)
        bb = draw.textbbox((0, 0), cta_palabra, font=kw_f)
        kx = (W - (bb[2] - bb[0])) // 2
        draw.text((kx + 2, y + 26 + 2), cta_palabra, font=kw_f, fill=(0, 0, 0, 120))
        draw.text((kx, y + 26), cta_palabra, font=kw_f, fill=YELLOW,
                  stroke_width=2, stroke_fill=YELLOW)
        y += box_h + 44
        # Subtítulo + cierre (texto_extra) + handle, autoajustados al resto del lienzo
        draw_fitted_block(draw, proj_dir, [
            {"text": subtitulo or "y te mando el tutorial completo.", "size": 56, "bold": False, "color": WHITE, "gap": 22},
            {"text": texto_extra, "size": 44, "bold": False, "color": DIM, "gap": 22},
            {"text": nombre_marca, "size": 50, "bold": True, "color": PRIMARY, "gap": 0},
        ], y_top=y, y_bottom=1850, anchor="top")

    else:
        # Slides genéricos: problema, revelacion, beneficios, prueba
        y_top, y_bottom = pick_text_band(img, slide.get("texto_pos", "auto"), bool(foto))
        draw_fitted_block(draw, proj_dir, [
            {"text": titulo,    "size": 68, "bold": True,  "color": WHITE,   "stroke": 1, "gap": 22},
            {"text": subtitulo, "size": 48, "bold": False, "color": PRIMARY, "stroke": 1, "gap": 18},
            {"text": texto_extra, "size": 40, "bold": False, "color": DIM,   "gap": 0},
        ], y_top=y_top, y_bottom=y_bottom)

    # ── Guardar ────────────────────────────────────────────────────────────────
    nombre = f"{idx:02d}-{tipo}.png"
    return save(img, output_dir, nombre)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, help="Ruta al plan.json")
    parser.add_argument("--proj-dir", default=".", help="Directorio raíz del proyecto")
    args = parser.parse_args()

    proj_dir = Path(args.proj_dir).resolve()
    _load_dotenv(proj_dir)
    cfg = load_config(proj_dir)
    colors = colors_from_config(cfg)

    plan = json.loads(Path(args.plan).read_text())
    slides = plan["slides"]
    total = len(slides)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    output_dir = proj_dir / "output" / f"historias_{ts}"
    output_dir.mkdir(parents=True, exist_ok=True)

    kie_key = cfg.get("kie_ai_key") or os.environ.get("KIE_AI_API_KEY")
    kie_cache: dict[str, Path] = {}

    # Pre-generar fondos AI en paralelo
    if kie_key:
        ai_slides = [(i, s) for i, s in enumerate(slides)
                     if s.get("fondo_ia") and not s.get("foto")]
        if ai_slides:
            print(f"\n→ Generando {len(ai_slides)} fondo(s) con IA en paralelo...")
            results: dict[int, str | None] = {}

            def gen(idx, slide):
                try:
                    prompt = slide["fondo_ia"]["prompt"]
                    url = kie_generate(prompt, kie_key)
                    if url:
                        dest = output_dir / f"_bg_{idx:02d}.png"
                        if download_image(url, dest):
                            results[idx] = dest
                            print(f"  ✅ Fondo IA slide {idx+1} listo")
                except Exception as e:
                    print(f"  ⚠️  Thread slide {idx+1} error: {e}")

            threads = [threading.Thread(target=gen, args=(i, s)) for i, s in ai_slides]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            for idx, slide in ai_slides:
                if idx in results:
                    key = slide["fondo_ia"]["prompt"]
                    kie_cache[key] = results[idx]

    print(f"\n→ Renderizando {total} slides...")
    for i, slide in enumerate(slides, 1):
        render_slide(slide, i, total, proj_dir, cfg, colors,
                     kie_cache, kie_key, output_dir)

    # Guardar copia del plan
    (output_dir / "plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False))

    print(f"\n✅ Historias generadas en: {output_dir}")
    return str(output_dir)


if __name__ == "__main__":
    main()
