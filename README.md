# 📲 Historias IG Skill — Claude Code

> Genera secuencias de **historias de Instagram profesionales** para tu negocio con un solo comando en Claude Code. Le dictas la idea, y la IA elige la estructura narrativa, escribe el copy y crea todas las imágenes.

Esta es una versión **mejorada y mantenida por [Diego Osorio (@soydiegoosorio)](https://instagram.com/soydiegoosorio)**, basada en el excelente trabajo original de **Horizontes IA** (ver [Créditos](#-créditos)).

---

## ✨ ¿Qué hace?

A partir de un tema, genera **5–7 slides listos para publicar** (1080×1920 px) con:

- 🧠 **Estructura narrativa** elegida automáticamente entre 35 fórmulas virales (hook → dolor → solución → demo → resultado → CTA).
- ✍️ **Copy persuasivo** adaptado a tu marca y objetivo (lead magnet, urgencia, prueba social, etc.).
- 🖼️ **Fondos** con tus propias fotos **o** generados con IA (Kie AI).
- 🎨 Tipografía de impacto con **tus colores de marca**.
- 🔑 **Palabra clave de CTA** lista para tu automatización de DMs.

---

## 🚀 Mejoras de esta versión

- 🔠 **Autoajuste de texto:** el copy largo se escala solo para que siempre quepa y se lea.
- 🎯 **Colocación inteligente:** el texto se ubica en la zona más despejada del fondo, **sin tapar tu cara**.
- 🔄 **Corrección de rotación EXIF:** las fotos de cámara/celular ya no salen giradas.
- 💸 **Modelo económico por defecto** (`google/nano-banana`, ~$0.02/img) y opción premium (`nano-banana-2`) para ocasiones especiales.
- 📲 **Envío a tu celular por Telegram:** cuando un set te gusta, te llega al teléfono para subirlo en segundos.
- ⚙️ **`.env` que sí funciona** (carga sin dependencias) y verbo de CTA configurable (“Comenta” / “Responde”).
- 🪟 **Compatibilidad con Windows nativo** mejorada (UTF-8, rutas).

---

## 📋 Requisitos

- [Claude Code](https://claude.com/claude-code) instalado
- **Python 3.10+**
- macOS, Linux o **Windows**
- *(Opcional)* Cuenta de [Kie AI](https://kie.ai) para fondos con IA
- *(Opcional)* Un bot de [Telegram](https://telegram.org) para recibir los sets en tu celular

---

## ⚡ Instalación

### Opción A — con Claude Code (recomendado)

Abre Claude Code, pega esto y envíalo:

```
Clona https://github.com/diegodoc11/historias-ig-skill.git en ~/historias-ig y corre el setup automáticamente según mi sistema operativo
```

Cuando termine, **cierra y vuelve a abrir Claude Code** para que detecte el skill.

### Opción B — manual

```bash
git clone https://github.com/diegodoc11/historias-ig-skill.git ~/historias-ig
cd ~/historias-ig
```

**macOS / Linux:**
```bash
chmod +x setup.sh && ./setup.sh
```

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\setup.ps1
```

Luego **reinicia Claude Code** para que aparezca el comando `/historias-ig`.

---

## 🔧 Configuración opcional

### Kie AI (fondos con IA)
Copia `.env.example` a `.env` y agrega tu clave:
```
KIE_AI_API_KEY=tu_clave_aqui
```
Sin esto, el skill funciona perfecto usando tus propias fotos.

### Telegram (recibir los sets en tu celular)
1. En Telegram, crea un bot con **@BotFather** (`/newbot`) y copia el **token**.
2. Pégalo en `.env`:
   ```
   TELEGRAM_BOT_TOKEN=tu_token_aqui
   ```
3. Escríbele “hola” a tu bot y obtén tu *chat id*:
   ```bash
   python scripts/telegram_enviar.py --proj-dir . --get-chat-id
   ```
4. Pega el chat id en `.env` (`TELEGRAM_CHAT_ID=...`).
5. Para enviarte el último set generado:
   ```bash
   python scripts/telegram_enviar.py --proj-dir .
   ```
   *(añade `--doc` para calidad original sin compresión)*

---

## 🎬 Uso

```
/historias-ig
```

La **primera vez** te hace unas preguntas sobre tu marca (nombre, colores, CTA…) y se configura. Después, solo dile el **tema + objetivo** del día y genera el set en `output/`.

| Comando | Qué hace |
|---|---|
| `/historias-ig` | Genera las historias del día |
| `/historias-ig reconfigurar` | Cambia los datos de tu marca |
| `/historias-ig fotos` | Re-escanea tus fotos disponibles |
| `/historias-ig ver` | Abre la última carpeta de output |

---

## 📁 Estructura

```
historias-ig/
├── fotos/            ← Pon aquí tus fotos (JPG, PNG, WEBP)
├── output/           ← Las historias generadas aparecen aquí
├── scripts/
│   ├── generate.py        ← Motor de generación de imágenes
│   ├── scan_fotos.py      ← Escanea y cataloga tus fotos
│   ├── utils.py           ← Funciones de renderizado
│   └── telegram_enviar.py ← Envía un set a tu celular vía Telegram
├── skill/historias-ig.md  ← El skill de Claude Code
├── .env                   ← Tus claves (NO se sube a git)
└── config.json            ← Tu configuración de marca (se crea al primer uso)
```

> 🔒 **Privacidad:** `.env`, `config.json` y la carpeta `fotos/` están en `.gitignore`. Tus claves y fotos **nunca** se suben a GitHub.

---

## 🪟 Nota para Windows

Si al ejecutar ves un error de “Python no encontrado” aunque lo tengas instalado, desactiva los *alias de la Microsoft Store*: **Configuración → Aplicaciones → Alias de ejecución de aplicaciones →** apaga `python.exe` y `python3.exe`. (O instala Python desde [python.org](https://python.org) marcando “Add to PATH”.)

---

## 🙏 Créditos

- **Skill original:** [Horizontes IA](https://horizontesia.com) — academia de IA y automatización en español · repo original: [github.com/santmun/historias-ig-skill](https://github.com/santmun/historias-ig-skill). Todo el crédito de la idea y la base es suyo.
- **Versión mejorada y mantenida por:** [Diego Osorio — @soydiegoosorio](https://instagram.com/soydiegoosorio).

Si esta skill te sirve, sígueme en [@soydiegoosorio](https://instagram.com/soydiegoosorio) para más automatizaciones con IA. 🚀
