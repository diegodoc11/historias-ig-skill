#!/usr/bin/env python3
"""
telegram_enviar.py — Envía un set de historias al celular vía un bot de Telegram.

Uso:
  # 1) Obtener tu chat id (despues de escribirle "hola" a tu bot):
  python telegram_enviar.py --proj-dir <PROJ> --get-chat-id

  # 2) Enviar el ultimo set generado:
  python telegram_enviar.py --proj-dir <PROJ>

  # Enviar un set especifico (carpeta dentro de output/):
  python telegram_enviar.py --proj-dir <PROJ> --set historias_2026-05-22_1611

  # Enviar en calidad original (como archivo, sin compresion):
  python telegram_enviar.py --proj-dir <PROJ> --doc

Token y chat id se leen de config.json (telegram_bot_token / telegram_chat_id)
o de las variables de entorno TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID.
"""

import argparse
import json
import sys
import time
import uuid
import urllib.request
import urllib.error
from pathlib import Path


def _api(token, method, fields=None, files=None, timeout=60):
    url = f"https://api.telegram.org/bot{token}/{method}"
    if not files:
        data = json.dumps(fields or {}).encode()
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"})
    else:
        boundary = uuid.uuid4().hex
        body = b""
        for k, v in (fields or {}).items():
            body += (f"--{boundary}\r\nContent-Disposition: form-data; "
                     f"name=\"{k}\"\r\n\r\n{v}\r\n").encode()
        for name, filename, content in files:
            body += (f"--{boundary}\r\nContent-Disposition: form-data; "
                     f"name=\"{name}\"; filename=\"{filename}\"\r\n"
                     f"Content-Type: application/octet-stream\r\n\r\n").encode()
            body += content + b"\r\n"
        body += f"--{boundary}--\r\n".encode()
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def load_creds(proj_dir):
    import os
    # Cargar .env si existe (sin dependencias externas)
    envp = proj_dir / ".env"
    if envp.exists():
        for line in envp.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    cfg_path = proj_dir / "config.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        token = token or cfg.get("telegram_bot_token")
        chat_id = chat_id or cfg.get("telegram_chat_id")
    return token, chat_id


def latest_set(proj_dir):
    out = proj_dir / "output"
    sets = sorted([d for d in out.glob("historias_*") if d.is_dir()])
    return sets[-1] if sets else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj-dir", default=".")
    ap.add_argument("--set", default=None, help="Nombre de carpeta dentro de output/")
    ap.add_argument("--get-chat-id", action="store_true")
    ap.add_argument("--doc", action="store_true", help="Enviar como archivo (calidad original)")
    args = ap.parse_args()

    proj_dir = Path(args.proj_dir).resolve()
    token, chat_id = load_creds(proj_dir)

    if not token:
        print("❌ Falta el token. Agrega 'telegram_bot_token' en config.json.")
        sys.exit(1)

    if args.get_chat_id:
        r = _api(token, "getUpdates")
        chats = {}
        for upd in r.get("result", []):
            msg = upd.get("message") or upd.get("channel_post") or {}
            ch = msg.get("chat")
            if ch:
                chats[ch["id"]] = ch.get("first_name") or ch.get("title") or ch.get("username") or "?"
        if chats:
            print("✅ Chats encontrados (escribe el id en config.json -> telegram_chat_id):")
            for cid, name in chats.items():
                print(f"   chat_id = {cid}   ({name})")
        else:
            print("⚠️  No hay mensajes recientes. Escríbele 'hola' a tu bot y reintenta.")
        return

    if not chat_id:
        print("❌ Falta el chat id. Corre con --get-chat-id primero.")
        sys.exit(1)

    set_dir = (proj_dir / "output" / args.set) if args.set else latest_set(proj_dir)
    if not set_dir or not set_dir.exists():
        print(f"❌ No encontré el set: {set_dir}")
        sys.exit(1)

    slides = sorted(set_dir.glob("0*.png"))
    if not slides:
        print(f"❌ No hay slides (0*.png) en {set_dir}")
        sys.exit(1)

    _api(token, "sendMessage", {
        "chat_id": chat_id,
        "text": f"📲 Set listo: {set_dir.name} — {len(slides)} historias (en orden). "
                f"Guárdalas a la galería y súbelas a tus historias."
    })

    method = "sendDocument" if args.doc else "sendPhoto"
    field = "document" if args.doc else "photo"
    ok = 0
    for i, s in enumerate(slides, 1):
        content = s.read_bytes()
        r = _api(token, method,
                 fields={"chat_id": chat_id, "caption": f"{i}/{len(slides)}"},
                 files=[(field, s.name, content)])
        if r.get("ok"):
            ok += 1
            print(f"  ✅ Enviado {i}/{len(slides)}: {s.name}")
        else:
            print(f"  ⚠️  Error en {s.name}: {r.get('description')}")
        time.sleep(0.4)

    print(f"\n✅ {ok}/{len(slides)} historias enviadas a tu Telegram.")


if __name__ == "__main__":
    main()
