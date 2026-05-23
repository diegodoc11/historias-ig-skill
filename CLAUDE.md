# CLAUDE.md — Guía del proyecto

Generador de **historias y carruseles de Instagram** para Claude Code. El usuario dicta una idea; la skill elige el tipo de contenido, escribe el copy persuasivo y renderiza las imágenes listas para publicar.

## ⚠️ Regla de oro
**Nunca generes imágenes sin que el usuario apruebe el copy exacto de cada slide.** Muestra el copy (título, subtítulo, texto extra, CTA, etiqueta) slide por slide, espera el OK explícito, y solo entonces ejecuta `generate.py`. Generar sin aprobación causa errores y gasta créditos de IA.

## Estructura
```
skill/historias-ig.md        ← Cerebro de la skill (flujo, onboarding, reglas)
skill/biblioteca-contenido.md← 8 tipos de contenido (estructura, persuasión, ganchos, CTA)
scripts/generate.py          ← Motor de render (lee plan.json → PNG en output/)
scripts/scan_fotos.py        ← Cataloga fotos/ → catalogo.json
scripts/utils.py             ← Pipeline de imagen (fondos, texto, guardado)
scripts/telegram_enviar.py   ← Envía un set al celular vía bot de Telegram
config.json                  ← Marca + brief (privado, en .gitignore)
fotos/  output/  fonts/  logos/   (todos en .gitignore)
```

## Flujo de generación
1. Leer `config.json` (marca + brief). Si no existe → onboarding (ver skill).
2. Pedir **tema + objetivo**.
3. Leer `skill/biblioteca-contenido.md` y elegir el **tipo** según el objetivo.
4. Escanear fotos (`scan_fotos.py`); consultar `catalogo_detallado.json` si existe.
5. Escribir el **plan.json** (un objeto por slide) y **mostrar el copy para aprobación**.
6. Tras el OK: `python scripts/generate.py --plan plan.json --proj-dir .`
7. Mostrar resultados y ofrecer envío por Telegram (`telegram_enviar.py`).

## Formato del plan (campos por slide)
`tipo` (`hook`/`cta`/descriptivo), `titulo`, `subtitulo`, `texto_extra`, `foto`,
`fondo_ia:{prompt}`, `texto_pos` (`auto`/`top`/`center`/`bottom`), `etiqueta` (hook),
`logos` (lista de marcas), `palabras_clave`, `cta_palabra`, `cta_verbo`.

## Convenciones del motor
- **Lienzo:** historia 1080×1920 (9:16). Texto: título blanco, subtítulo en color primario, extra en gris.
- **Autoajuste:** el texto escala para caber; **colocación inteligente** evita tapar la cara (banda más oscura).
- **Fondos:** foto real (respeta EXIF) → IA (Kie, `google/nano-banana` económico; `nano-banana-2` premium) → sólido.
- **Chips de marca:** `logos:[...]` usa `logos/<slug>.png` si existe; si no, muestra el nombre.
- **CTA:** `Comenta [PALABRA] y te envío [recurso]`. Palabra en MAYÚSCULAS, 3–8 letras, sin acentos.
- **Ejecutar siempre con** `python -X utf8` (la consola puede no ser UTF-8).

## Claves
`KIE_AI_API_KEY` (fondos IA) y Telegram (`telegram_bot_token`, `telegram_chat_id`) en `.env` o `config.json`. Nunca subir secretos: `config.json`, `.env` y `fotos/` están en `.gitignore`.

## Comandos
`/historias-ig` (genera) · `reconfigurar` · `fotos` · `ver` · `enviar` (Telegram).
