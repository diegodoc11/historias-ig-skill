# /historias-ig — Generador de Contenido de Instagram

Genera secuencias de **historias** (y próximamente carruseles) de Instagram eligiendo el **tipo de contenido** y la **estructura persuasiva** más adecuados al objetivo del día, usando la Biblioteca de Contenido.

**Directorio del proyecto:** `{{PROJ_DIR}}`
**Biblioteca de contenido:** `{{PROJ_DIR}}/skill/biblioteca-contenido.md`

---

## FLUJO PRINCIPAL

### Al invocar `/historias-ig`

**Paso 1 — Verificar configuración**

Lee `{{PROJ_DIR}}/config.json`. Si no existe, ejecuta el **ONBOARDING** (ver abajo).

**Paso 2 — Pedir tema y objetivo**

Pregunta al usuario (en un solo mensaje):
> "¿Cuál es el tema de hoy? ¿Y qué objetivo buscas?"
>
> Objetivo — elige uno:
> - **Que me conozcan / conexión** (Relacionamiento)
> - **Alcance / llegar a más gente** (Engagement)
> - **Diferenciarme / romper un mito** (Polarización)
> - **Enseñar algo accionable** (Transformación)
> - **Abrir conversación / resolver dudas** (Interacción 1×1)
> - **Mover hacia la compra** (Niveles de Consciencia)
> - **Posicionarme / justificar mi precio** (Autoridad)
> - **Vender / lanzar** (Conversión)
> - **Libre** — Claude elige el tipo

Si el usuario no especifica objetivo, infiérelo del tema.

**Paso 3 — Elegir el tipo de contenido (Biblioteca)**

**Lee `{{PROJ_DIR}}/skill/biblioteca-contenido.md`.** Con el tema + objetivo, usa la tabla "objetivo → tipo" para elegir el **tipo REPTINAC** más adecuado. Toma de ahí su **estructura slide-por-slide**, su **ángulo de persuasión** y su **mecánica de interacción/CTA**.

Presenta al usuario:
> "Voy a usar **[TIPO]** ([para qué sirve]). La estructura será: [flujo en una línea]. ¿Continuamos?"

Si el usuario quiere otro, ofrece 2–3 alternativas justificadas y deja elegir.

**Paso 4 — Escanear fotos disponibles**

```bash
python3 {{PROJ_DIR}}/scripts/scan_fotos.py --proj-dir {{PROJ_DIR}} 2>/dev/null || python {{PROJ_DIR}}/scripts/scan_fotos.py --proj-dir {{PROJ_DIR}}
```
Para elegir fotos que NO tapen elementos importantes, consulta `{{PROJ_DIR}}/catalogo_detallado.json` si existe (describe contenido y zona de texto segura de cada foto).

**Paso 5 — Crear el plan de slides**

Sigue la estructura del tipo elegido en la biblioteca. Aplica **persuasión real**: dolor concreto (con consecuencia y horizonte), deseo, prueba, manejo de objeción, y un cierre con mecánica de interacción o palabra clave → recurso.

**Reglas por slide:**
- `tipo`: `hook` para el primero, `cta` para el último; nombres descriptivos para los intermedios (`problema`, `revelacion`, `paso1`, `voto`, etc.).
- `titulo`: frase de impacto (el motor ajusta el tamaño automáticamente; puedes escribir copy más largo).
- `subtitulo`: elaboración (se renderiza en el color primario de la marca).
- `texto_extra`: detalle secundario o cita (se renderiza en gris tenue).
- `foto`: archivo de `catalogo.json` que encaje (cara arriba, zona inferior despejada), o `null`.
- `fondo_ia`: `{"prompt": "..."}` (en inglés, oscuro + color de marca, zona inferior despejada para el texto) si hay Kie AI y no hay foto.
- `texto_pos`: `"auto"` (recomendado) | `"top"` | `"center"` | `"bottom"` — dónde poner el texto sin tapar la cara.
- `etiqueta`: (solo hook) etiqueta personalizada de la píldora superior (ej: "REGALO GRATIS"). Si se omite, usa la de config.
- `palabras_clave`: 1–3 palabras clave del slide (referencia).
- `cta_palabra`: solo en el slide `cta` — MAYÚSCULAS, 3–8 letras, sin acentos, temática.
- `cta_verbo`: solo en `cta` — "Comenta" / "Responde" (si se omite, usa el de config).

**Formato del plan JSON:**
```json
{
  "tipo_contenido": "Engagement (Top 5)",
  "objetivo": "alcance",
  "slides": [
    {
      "numero": 1, "tipo": "hook",
      "etiqueta": "TOP 5",
      "titulo": "Los 5 anuncios que más venden en estética",
      "subtitulo": "Guárdalo antes de tu próxima campaña.",
      "texto_extra": null,
      "foto": "foto.jpg", "fondo_ia": null,
      "texto_pos": "auto",
      "palabras_clave": ["5 anuncios"], "cta_palabra": null
    },
    {
      "numero": 7, "tipo": "cta",
      "titulo": "¿Quieres las 5 plantillas?",
      "subtitulo": "y te las envío en PDF, listas para usar.",
      "texto_extra": "Los negocios del futuro no se crean con herramientas del pasado.",
      "foto": null, "fondo_ia": null,
      "cta_palabra": "PLANTILLAS", "cta_verbo": "Comenta"
    }
  ]
}
```

**⚠️ REGLA DE ORO — aprobar el copy antes de generar:** Muestra al usuario el **copy EXACTO de cada slide** (título, subtítulo, texto extra, CTA, etiqueta) en texto legible, slide por slide. **Espera su aprobación explícita.** NUNCA ejecutes `generate.py` hasta que el usuario apruebe el copy. Si pide cambios, ajústalos y vuelve a mostrar el copy completo. Generar sin copy aprobado causa errores y desperdicia créditos de IA.

**Paso 6 — Guardar el plan y generar**

```bash
python3 {{PROJ_DIR}}/scripts/generate.py --plan {{PROJ_DIR}}/plan.json --proj-dir {{PROJ_DIR}} 2>/dev/null || python {{PROJ_DIR}}/scripts/generate.py --plan {{PROJ_DIR}}/plan.json --proj-dir {{PROJ_DIR}}
```

**Paso 7 — Mostrar resultados y publicar**

Muestra el slide 1 (hook) y el último (CTA). Abre la carpeta de output. Si el usuario aprueba el set, ofrece **enviarlo a su celular por Telegram**:
```bash
python3 {{PROJ_DIR}}/scripts/telegram_enviar.py --proj-dir {{PROJ_DIR}} 2>/dev/null || python {{PROJ_DIR}}/scripts/telegram_enviar.py --proj-dir {{PROJ_DIR}}
```

---

## TIPOS DE CONTENIDO

Los 8 tipos (Relacionamiento, Engagement, Polarización, Transformación, Interacción 1×1, Niveles de Consciencia, Autoridad, Conversión) con sus estructuras, persuasión, ganchos y CTA están en:

➡️ **`{{PROJ_DIR}}/skill/biblioteca-contenido.md`** (consúltala siempre en el Paso 3).

Tabla rápida objetivo → tipo:

| Objetivo | Tipo |
|---|---|
| Conexión / que me conozcan | Relacionamiento |
| Alcance | Engagement |
| Romper un mito / diferenciarme | Polarización |
| Enseñar (guardable) | Transformación |
| Conversación / dudas | Interacción 1×1 |
| Mover a la compra | Niveles de Consciencia |
| Posicionamiento / precio | Autoridad |
| Vender / lanzar | Conversión |

---

## REGLAS DE CTA

- Formato: `[Verbo] [PALABRA] y te [envío/mando] [recurso concreto]`.
- Palabra clave: una sola, MAYÚSCULAS, 3–8 caracteres, sin acentos, temática (no "INFO"/"HOLA").
- Nunca: "link en bio", "mándame DM", "Call to Action".
- Alterna mecánicas de interacción: voto por comentario, encuesta A/B, caja de dudas, etiquetado.

## REGLAS DE FONDOS

Orden de prioridad por slide:
1. **Foto real** del catálogo que encaje (cara arriba, zona inferior despejada — ver `catalogo_detallado.json`).
2. **Fondo IA** (Kie AI) con prompt en inglés, estilo oscuro + color de marca, zona inferior despejada.
3. **Fondo sólido** — último recurso (CTA suele ir sólido para que el texto domine).

El **hook** lleva el fondo más impactante. El texto se coloca solo en la zona despejada (`texto_pos: "auto"`).

---

## ONBOARDING (primer uso) — Brief de Marca

Si no existe `config.json`, construye el **brief**. El brief es lo que hace que el copy sea personalizado y persuasivo (sin él, el contenido sale genérico). Ofrece dos modos:

> "¿Llenamos tu brief en modo **LIBRE** (me cuentas tu negocio y tu historia como a un amigo, yo extraigo lo demás y solo te pregunto lo que falte) o **ESTRUCTURADO** (sección por sección)?"

### A. Identidad (siempre)
1. **Nombre de marca/negocio** → `nombre_marca`
2. **¿A qué se dedica? (1-2 oraciones)** → `descripcion_negocio`
3. **Tu nombre** → `nombre_usuario`
4. **Usuario de Instagram** → `instagram_user` (agrega @ si falta)
5. **Colores de marca:** a) hex (fondo + primario) · b) por defecto (oscuro-cyan) · c) `oscuro-cyan` (#08080F/#00E5FF) | `oscuro-naranja` (#0D0A08/#FF6B35) | `oscuro-verde` (#080F09/#00E676) | `claro-profesional` (#F8F9FA/#1A1A2E) → `colores`
6. **¿Kie AI?** Si sí, agregar `KIE_AI_API_KEY` en `{{PROJ_DIR}}/.env`.
7. **CTA habitual** (ej: "Comenta [PALABRA] y te envío [algo]") → `cta_formato`
8. **Etiqueta del hook por defecto** (ej: "HOY TE ENSEÑO") → `etiqueta_hook`

### B. Brief estratégico (para copy ultra-personalizado)
9. **Avatar / cliente ideal:** quién es (demografía + psicografía), su situación actual y qué quiere lograr → `avatar`
10. **Mapa de dolores (4 niveles)** → `dolores`:
    - **externo:** el problema visible/práctico.
    - **interno:** cómo lo hace sentir (frustración, miedo, vergüenza).
    - **relacional:** cómo afecta su estatus/relaciones.
    - **filosófico:** la injusticia profunda. *Debe pasar el Test de Amenaza Concreta:* ¿qué le pasa, en cuánto tiempo, si no lo resuelve? (concreto, no abstracto).
11. **Deseos / transformación buscada** → `deseos`
12. **Banco de auto-aplicación:** 3–8 momentos en que lo que vendes te ayudó a ti mismo (para Relacionamiento y Niveles de Consciencia) → `banco_auto_aplicacion` (lista)
13. **Creencias del nicho:** mitos populares, verdades incómodas, prácticas saturadas con las que no estás de acuerdo (para Polarización) → `creencias_nicho` (lista)
14. **Oferta principal + ticket:** qué vendes y rango de precio (low <$300 / mid $300–$1.000 / high >$1.000) → `oferta` (activa las reglas de precio en Conversión)
15. **Tono/voz:** frases que repites, registro (cercano/técnico), qué evitar → `tono`

Si el usuario tiene poco tiempo, captura mínimo: identidad (A) + avatar + dolores + 3 momentos de banco. El resto se puede completar después con `/historias-ig reconfigurar`.

Crear `{{PROJ_DIR}}/config.json`:
```json
{
  "nombre_marca": "...",
  "descripcion_negocio": "...",
  "nombre_usuario": "...",
  "instagram_user": "@...",
  "etiqueta_hook": "...",
  "colores": { "fondo": "#0D0A08", "primario": "#FF6B35" },
  "kie_ai_key": null,
  "cta_formato": "Comenta [PALABRA] y te envío [algo]",
  "avatar": "...",
  "dolores": { "externo": "...", "interno": "...", "relacional": "...", "filosofico": "..." },
  "deseos": "...",
  "banco_auto_aplicacion": ["...", "..."],
  "creencias_nicho": ["...", "..."],
  "oferta": { "descripcion": "...", "ticket": "low | mid | high" },
  "tono": "..."
}
```

> 📌 **Uso del brief al crear contenido (Paso 5):** Relacionamiento → usa `banco_auto_aplicacion`; Polarización → usa `creencias_nicho`; Niveles de Consciencia → usa `dolores` (agita el dolor concreto); Conversión → usa `oferta` + reglas de precio; Autoridad → usa credenciales/casos; siempre habla al `avatar` con su `tono`.

Luego escanea fotos (Paso 4). Si no hay fotos, indica agregarlas en `{{PROJ_DIR}}/fotos/`.

---

## COMANDOS DE UTILIDAD

- **`/historias-ig reconfigurar`** → borra `config.json` y rehace el onboarding.
- **`/historias-ig fotos`** → re-escanea la carpeta de fotos.
- **`/historias-ig ver`** → abre la última carpeta de output.
- **`/historias-ig enviar`** → manda el último set a tu celular por Telegram.

---

## NOTAS TÉCNICAS

- **Fuentes:** Space Grotesk (en `{{PROJ_DIR}}/fonts/`).
- **Historia:** 1080×1920 (9:16). **Carrusel:** 1080×1350 (4:5) *(próximamente)*.
- **Texto:** autoajuste de tamaño + colocación inteligente (no tapa la cara).
- **Kie AI:** modelo económico `google/nano-banana` por defecto; `nano-banana-2` para ocasiones especiales.
- **Telegram:** envía el set al celular para publicarlo (ver `.env` o `config.json`).
