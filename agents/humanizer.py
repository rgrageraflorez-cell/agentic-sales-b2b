"""
HumanizerAgent — Agente 14
Elimina señales de escritura generada por IA en los emails redactados.
Basado en blader/humanizer (github.com/blader/humanizer) y el
Wikipedia:Signs_of_AI_writing guide de WikiProject AI Cleanup.

Pipeline: Copywriter → Humanizer → Sender
"""

from .base import BaseAgent
from models import EmailDraft


# ── Patrones a eliminar (referencia del skill blader/humanizer) ─────────────

HUMANIZER_SYSTEM = """
Eres un editor profesional de español de España especializado en correspondencia
comercial B2B formal. Tu trabajo es pulir emails de ventas para que suenen naturales,
serios y profesionales, como los escribiría un consultor senior con años de experiencia.

OBJETIVO: mantener un tono FORMAL y serio (tratamiento de usted), longitud similar
al original (no acortar nunca por debajo de 220 palabras), y eliminar cualquier
patrón de escritura de IA o error ortográfico.

PATRONES QUE DEBES ELIMINAR:

1. PALABRAS DE SIGNIFICANCIA INFLADA
   Elimina: "es un testimonio de", "papel fundamental", "subraya la importancia",
   "refleja una tendencia más amplia", "marca un hito", "en el dinámico panorama",
   "punto de inflexión", "marca indeleble", "profundamente arraigado"

2. LENGUAJE PROMOCIONAL Y DE MARKETING
   Elimina: "innovador", "revolucionario", "de vanguardia", "sin fisuras",
   "potente", "robusto", "completo", "holístico", "sinérgico", "solución integral"

3. FRASES CON -NDO SUPERFICIALES
   Reescribe: "destacando que...", "subrayando...", "reflejando...",
   "contribuyendo a...", "fomentando...", "mostrando..."

4. PALABRAS COMODÍN DE IA
   Elimina: "aprovechar", "navegar", "profundizar", "desbloquear", "transformar",
   "empoderar", "elevar", "impulsar el crecimiento", "panorama competitivo",
   "caso de uso", "ecosistema"

5. ARTEFACTOS DE CHATBOT
   Elimina: "¡Claro!", "Por supuesto", "Espero que esto ayude",
   "No dudes en contactarme"

6. GUIONES EM EN EXCESO
   Sustitúyelos por comas o puntos.

7. FINALES GENÉRICOS
   Evita: "El futuro es prometedor", "Estamos deseando colaborar".
   Mantén un cierre formal concreto.

REVISIÓN ORTOGRÁFICA Y GRAMATICAL (OBLIGATORIA):
- Verifica todas las tildes: análisis, decisión, predicción, gestión, visión, más,
  sólo/solo, qué/que, cómo/como, dónde/donde, quién/quien.
- Verifica "si" (condicional) vs "sí" (afirmación); "tu" (posesivo) vs "tú" (pronombre);
  "mas" (pero) vs "más" (cantidad).
- Corrige signos de apertura ¿ y ¡ si se usan cierre sin apertura.
- Concordancia de género y número. Conjugación verbal correcta.
- Uso adecuado de puntos, comas y punto y coma.

REGLAS DE TONO FORMAL B2B (CRÍTICAS):
- Tratamiento de USTED en todo momento. NUNCA utilice: tú, te, ti, tuyo/a, contigo,
  vosotros, os, vuestro/a, "estás", "puedes", "quieres", "tienes", "sabes".
- Use siempre: usted/ustedes, le/les, su/sus, está, puede, quiere, tiene, sabe.
- Antes de devolver el email, revise cada verbo: todos deben estar en 3ª persona
  del singular o del plural ("le propongo", "les ayudaría", "podría reservar").
- Sustituya cualquier "estás interesado" por "está interesado" o "si le interesa".
- Sustituya cualquier "te propongo" por "le propongo".
- Saludo formal: "Estimado/a [nombre]:" o "Estimados señores:".
- Despedida formal: "Reciba un cordial saludo," o "Atentamente,".
- Frases completas y bien construidas. Sin oraciones cortas tipo slogan.
- Vocabulario profesional pero accesible, sin jerga excesiva.

REGLAS DE LONGITUD Y CONTENIDO:
- El cuerpo debe mantener entre 220 y 320 palabras. NO acortes agresivamente.
- Conserva los 4 bloques: apertura personalizada, observación del sector,
  propuesta de ARIGRA, cierre con CTA.
- Mantén la información específica de la empresa destinataria.
- Un solo servicio de ARIGRA destacado, el más relevante.
- Sin precios, sin enlaces, sin emojis, sin signos de exclamación.

PROCESO:
1. Lee el email original completo.
2. Identifica patrones de IA y errores ortográficos o gramaticales.
3. Reescribe manteniendo la estructura, longitud y tono formal.
4. Revisa dos veces la ortografía y la gramática.
5. Devuelve el JSON con el email pulido, sin explicaciones.
"""


class HumanizerAgent(BaseAgent):
    """
    Reescribe emails generados por el Copywriter para eliminar
    señales de escritura de IA. Aplica los 24+ patrones del
    blader/humanizer skill basado en Wikipedia:Signs_of_AI_writing.
    """

    def __init__(self):
        super().__init__(
            name="Humanizador",
            description="Elimina señales de escritura IA en emails — basado en blader/humanizer",
        )

    async def execute(self, drafts: list[EmailDraft]) -> list[EmailDraft]:
        """Humaniza cada borrador de email."""
        self.log_step("Humanizando emails", f"{len(drafts)} emails")

        humanized = []
        for i, draft in enumerate(drafts):
            self.log_step(
                f"Humanizando {i+1}/{len(drafts)}",
                draft.recipient_name or draft.company_id,
            )
            try:
                humanized_draft = await self._humanize(draft)
                humanized.append(humanized_draft)
            except Exception as e:
                self.logger.error(f"Error humanizando {draft.company_id}: {e}")
                humanized.append(draft)  # fallback: usar original

        self.log_step("Humanización completada", f"{len(humanized)} emails procesados")
        return humanized

    async def _humanize(self, draft: EmailDraft) -> EmailDraft:
        """Aplica el proceso de humanización a un email."""

        prompt = f"""Pule este email de ventas B2B. Mantén el tono FORMAL (tratamiento de usted),
la estructura de 4 párrafos y una longitud entre 220 y 320 palabras.
Corrige cualquier error ortográfico o gramatical y elimina patrones de escritura IA.
NO acortes el email. NO cambies el tono a informal.

Devuelve SOLO el email final en este formato JSON exacto:

{{
  "subject": "asunto profesional pulido (entre 40 y 70 caracteres, sin ARIGRA, sin signos de exclamación)",
  "body_text": "cuerpo pulido con saltos de línea entre párrafos (220-320 palabras, tono formal de usted)"
}}

EMAIL ORIGINAL:
ASUNTO: {draft.subject}

{draft.body_text}

CONTEXTO:
- Empresa destinataria: {draft.company_name}
- Nombre del contacto: {draft.recipient_name or 'sin nombre'}
- Objetivo: correspondencia comercial B2B formal y profesional en español de España
"""

        result = await self.llm_call(
            prompt=prompt,
            system=HUMANIZER_SYSTEM,
            temperature=0.4,   # baja para preservar formalidad y precisión
            max_tokens=1600,
            response_format="json",
        )

        if isinstance(result, dict):
            if "subject" in result and result["subject"].strip():
                draft.subject = result["subject"].strip()
            if "body_text" in result and result["body_text"].strip():
                draft.body_text = result["body_text"].strip()
                draft.body_html = result["body_text"].strip().replace("\n", "<br>")

        return draft
