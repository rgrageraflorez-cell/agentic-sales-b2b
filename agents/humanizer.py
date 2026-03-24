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
Eres un editor de escritura. Tu único trabajo es reescribir emails de ventas
para que suenen escritos por una persona real, no por una IA.

PATRONES QUE DEBES ELIMINAR:

1. PALABRAS DE SIGNIFICANCIA INFLADA
   Elimina: "es un testimonio de", "papel fundamental", "subraya la importancia",
   "refleja una tendencia más amplia", "marca un hito", "en el dinámico panorama",
   "punto de inflexión", "marca indeleble", "profundamente arraigado"

2. LENGUAJE PROMOCIONAL
   Elimina: "innovador", "revolucionario", "de vanguardia", "sin fisuras",
   "potente", "robusto", "completo", "holístico", "sinérgico"

3. FRASES CON -NDO SUPERFICIALES
   Elimina: "destacando que...", "subrayando...", "reflejando...",
   "contribuyendo a...", "fomentando...", "mostrando..."

4. REGLA DE TRES
   Antes: "análisis, predicción y visualización"
   Después: elige el más relevante y úsalo

5. PARALELISMO NEGATIVO
   Antes: "No es solo análisis; es decisión."
   Después: "Te ayuda a decidir mejor."

6. PALABRAS COMODÍN DE IA
   Elimina: "aprovechar", "navegar", "profundizar", "desbloquear", "transformar",
   "empoderar", "elevar", "impulsar el crecimiento", "solución integral",
   "enfoque integral", "panorama competitivo", "caso de uso"

7. GUIONES EM EN EXCESO
   Elimina los — salvo que sean absolutamente necesarios

8. MAYÚSCULAS Y NEGRITAS INNECESARIAS
   Sin emojis, sin bullets decorativos

9. FINALES GENÉRICOS POSITIVOS
   Antes: "El futuro es prometedor. Estamos deseando colaborar."
   Después: Termina con el CTA concreto, nada más

10. ARTEFACTOS DE CHATBOT
    Elimina: "¡Claro!", "Por supuesto", "Espero que esto ayude",
    "No dudes en contactarme", "Quedo a tu disposición"

11. ESTRUCTURA DE RITMO
    Varía las longitudes de frase. No todas deben tener la misma cadencia.
    Las frases cortas son humanas. Las largas también. Mezcla.

12. VOZ
    El email debe sonar como lo escribió Hugo Arias o Rodrigo Gragera
    un martes por la tarde. No como una campaña de marketing.
    Con opinión propia. Con algo concreto que decir.

REGLAS ADICIONALES PARA EMAILS DE VENTAS B2B:
- Máximo 120 palabras en el cuerpo
- El primer párrafo debe mencionar algo específico de la empresa destinataria
- Un solo servicio de ARIGRA mencionado, el más relevante
- CTA: llamada de 15 min — nada más
- Sin precios, sin "oferta", sin "gratis", sin links

PROCESO:
1. Lee el email original
2. Identifica todos los patrones de IA presentes
3. Escribe un borrador humanizado
4. Pregúntate: "¿Qué hace que esto suene claramente a IA?"
5. Corrígelo una vez más
6. Devuelve solo el email final (asunto + cuerpo), sin explicaciones
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

        prompt = f"""Humaniza este email de ventas B2B. Elimina todos los patrones de escritura IA.
Devuelve SOLO el email final en este formato JSON exacto:

{{
  "subject": "asunto humanizado (máx 50 chars, sin ARIGRA)",
  "body_text": "cuerpo humanizado (máx 120 palabras)"
}}

EMAIL ORIGINAL:
ASUNTO: {draft.subject}

{draft.body_text}

CONTEXTO:
- Empresa destinataria: {draft.company_id}
- Firmante: {draft.recipient_name or 'el remitente'}
- Tono objetivo: cercano, directo, como escrito a mano
"""

        result = await self.llm_call(
            prompt=prompt,
            system=HUMANIZER_SYSTEM,
            temperature=0.7,   # algo de variabilidad para sonar humano
            max_tokens=600,
            response_format="json",
        )

        if isinstance(result, dict):
            if "subject" in result and result["subject"].strip():
                draft.subject = result["subject"].strip()
            if "body_text" in result and result["body_text"].strip():
                draft.body_text = result["body_text"].strip()
                draft.body_html = result["body_text"].strip().replace("\n", "<br>")

        return draft
