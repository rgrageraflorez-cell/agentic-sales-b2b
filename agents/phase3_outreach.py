"""
Fase 3: Agentes de outreach personalizado — adaptados a ARIGRA.
- CopywriterAgent: Genera emails personalizados con el enfoque de ARIGRA
- SenderAgent: Envía emails con rate limiting y rotación de firmantes
- FollowUpAgent: Gestiona seguimiento con estrategia progresiva
"""

from __future__ import annotations
import asyncio
import os
import random
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from dotenv import load_dotenv

from agents.base import BaseAgent
from models import (
    ClusterProfile, Company, EmailDraft, EmailTone, LeadStatus,
)

load_dotenv()


# ─── Contexto de ARIGRA (inyectado en cada prompt) ──────────

ARIGRA_CONTEXT = """
=== SOBRE ARIGRA ===
ARIGRA ayuda a empresas a convertir sus datos de ventas en decisiones útiles de negocio.

Lo que hacemos (3 pilares):
1. ENTENDER EL NEGOCIO A PARTIR DE LOS DATOS
   Analizamos evolución de ventas, productos, marcas, zonas geográficas, clientes y cualquier
   variable relevante. Detectamos patrones, oportunidades, caídas de rendimiento y diferencias
   entre líneas de negocio.

2. PREDECIR LA DEMANDA FUTURA
   Aplicamos modelos estadísticos y predictivos adaptados a cada caso:
   - Series temporales para prever ventas futuras cuando hay histórico temporal
   - Modelos de regresión para entender qué factores explican las ventas entre tiendas/productos/territorios
   - Curvas de adopción para estimar crecimiento de productos nuevos
   - Modelos ensamblados o redes neuronales cuando la complejidad lo requiere
   No usamos siempre el mismo modelo: elegimos el enfoque según el tipo de datos y el objetivo.

3. TRANSFORMAR EL ANÁLISIS EN HERRAMIENTAS PRÁCTICAS
   Entregamos informes claros, dashboards y visualizaciones para que dirección, ventas o marketing
   no dependan de hojas de cálculo complejas. Visión clara de qué vender, dónde poner el foco
   y cómo anticiparse.

=== PROPUESTA DE VALOR DIFERENCIAL ===
ARIGRA no aplica una solución estándar. Adapta el análisis y el modelo al tipo de problema,
al histórico disponible y al objetivo real del negocio. Ese enfoque flexible y técnico
(análisis transversal, series temporales, producto nuevo, combinación) nos diferencia
de consultoras que venden dashboards genéricos.

=== LO QUE NO SOMOS ===
- No somos una herramienta SaaS de BI (no vendemos licencias de software)
- No hacemos "gráficos bonitos" sin análisis detrás
- No aplicamos el mismo modelo a todos los clientes

=== CLIENTE IDEAL ===
Pymes y negocios que tienen datos de ventas (aunque sea en Excel) pero no los están
aprovechando para tomar decisiones. También empresas medianas y grandes que necesitan
ir más allá de los informes básicos que ya tienen.

=== FIRMANTES ===
Hugo Arias — Co-fundador de ARIGRA
Rodrigo Gragera — Co-fundador de ARIGRA
"""


# ─── Agente Copywriter ───────────────────────────────────────

class CopywriterAgent(BaseAgent):
    """Genera emails de prospección personalizados con el enfoque ARIGRA."""

    def __init__(self):
        super().__init__(
            name="Copywriter ARIGRA",
            description="Genera emails de venta personalizados para ARIGRA",
        )
        self.senders = self._load_senders()

    def _load_senders(self) -> list[dict]:
        """Carga los firmantes disponibles."""
        senders = [
            {
                "name": os.getenv("SENDER_NAME", "Hugo Arias"),
                "role": os.getenv("SENDER_ROLE", "Co-fundador"),
                "email": os.getenv("SENDER_EMAIL", "hugo@arigra.com"),
            }
        ]
        alt_name = os.getenv("SENDER_ALT_NAME")
        if alt_name:
            senders.append({
                "name": alt_name,
                "role": os.getenv("SENDER_ALT_ROLE", "Co-fundador"),
                "email": os.getenv("SENDER_ALT_EMAIL", "rodrigo@arigra.com"),
            })
        return senders

    def _pick_sender(self) -> dict:
        """Alterna entre firmantes para distribuir la carga."""
        return random.choice(self.senders)

    async def execute(
        self,
        companies: list[Company],
        cluster_profiles: list[ClusterProfile],
    ) -> list[EmailDraft]:
        """Genera emails para todas las empresas."""
        self.log_step("Generando emails ARIGRA", f"{len(companies)} empresas")

        profile_map = {p.cluster_id: p for p in cluster_profiles}
        drafts: list[EmailDraft] = []

        for i, company in enumerate(companies):
            self.log_step(f"Email {i+1}/{len(companies)}", company.name)

            profile = profile_map.get(company.cluster_id)
            if not profile:
                continue

            recipient_email = self._get_best_email(company)
            if not recipient_email:
                self.logger.debug(f"Sin email para {company.name}, saltando")
                continue

            recipient_name = ""
            if company.contacts:
                recipient_name = company.contacts[0].name

            try:
                draft = await self._generate_email(company, profile, recipient_email, recipient_name)
                drafts.append(draft)
                company.status = LeadStatus.EMAIL_DRAFTED
            except Exception as e:
                self.logger.error(f"Error generando email para {company.name}: {e}")

        self.log_step("Emails generados", f"{len(drafts)} emails listos")
        return drafts

    def _get_best_email(self, company: Company) -> str:
        """Obtiene el mejor email de contacto."""
        for contact in company.contacts:
            if contact.email and "@" in contact.email:
                return contact.email
        return company.email

    async def _generate_email(
        self,
        company: Company,
        profile: ClusterProfile,
        recipient_email: str,
        recipient_name: str,
    ) -> EmailDraft:
        """Genera un email personalizado con el enfoque ARIGRA."""

        sender = self._pick_sender()
        hook_context = self._build_hook_context(company)

        tone_instructions = {
            EmailTone.FORMAL: "Tono profesional y de usted. Lenguaje preciso, sin coloquialismos.",
            EmailTone.FRIENDLY: "Tono cercano, de tú. Natural, como si escribiera un conocido del sector. Sin ser forzado.",
            EmailTone.DIRECT: "Ir al grano. Primer párrafo = contexto en 1 frase. Segundo = qué hacemos. Tercero = CTA. Nada más.",
            EmailTone.CONSULTATIVE: "Empezar con una pregunta que haga pensar. Posicionarse como experto que quiere entender su caso antes de proponer.",
        }

        prompt = f"""{ARIGRA_CONTEXT}

=== TAREA ===
Genera un email de prospección B2B para la siguiente empresa.
El email debe parecer escrito por una persona real, no por una máquina.

=== DESTINATARIO ===
Empresa: {company.name}
Sector: {company.sector.value if company.sector else 'no definido'}
Tamaño: {company.size.value if company.size else 'no definido'} ({company.employee_count or '?'} empleados)
Ciudad: {company.city or 'desconocida'}
Productos/servicios que venden: {', '.join(company.products_services[:5]) if company.products_services else 'no conocidos'}
Tecnologías/herramientas: {', '.join(company.technologies_used[:5]) if company.technologies_used else 'no conocidas'}
Nombre contacto: {recipient_name or 'no disponible'}
Rating Google: {company.google_rating or 'desconocido'} ({company.google_reviews or '?'} reseñas)

=== GANCHO PERSONALIZADO ===
{hook_context}

=== ESTRATEGIA DEL CLUSTER ===
Perfil: {profile.description}
Pain points del segmento: {', '.join(profile.key_pain_points)}
Propuestas de valor a destacar: {', '.join(profile.value_propositions)}

=== INSTRUCCIONES DE REDACCIÓN ===
Tono: {tone_instructions.get(profile.recommended_tone, tone_instructions[EmailTone.FRIENDLY])}
Firmante: {sender['name']}, {sender['role']} de ARIGRA

REGLAS ESTRICTAS:
1. Asunto: máximo 50 caracteres. Que genere curiosidad SIN ser clickbait. Nunca usar "ARIGRA" en el asunto.
2. Cuerpo: máximo 120 palabras. Cada frase debe aportar.
3. Primer párrafo: demostrar que conoces algo concreto de SU empresa (producto, sector, situación).
4. Segundo párrafo: conectar ESO con lo que ARIGRA puede hacer por ellos. Ser específico sobre qué tipo de análisis o predicción les serviría. NO enumerar los 3 pilares — elegir el más relevante.
5. CTA: proponer una llamada breve de 15 min. Sin presión.
6. PROHIBIDO: "solución integral", "líder en", "innovador", "disruptivo", "oferta", "gratis", "sin compromiso", emojis.
7. PROHIBIDO: adjuntar links, PDFs o mencionar precios.
8. El email debe sonar como si Hugo o Rodrigo lo hubieran escrito a mano.
9. Si el destinatario tiene nombre, usarlo. Si no, empezar con "Buenas" o "Hola".

Devuelve SOLO JSON:
{{
    "subject": "Asunto del email",
    "body_text": "Cuerpo en texto plano con saltos de línea",
    "body_html": "Cuerpo en HTML simple (solo <p>, <br>, <b>)",
    "personalization_notes": "Qué datos de la empresa usaste para personalizar y por qué elegiste ese ángulo"
}}"""

        result = await self.llm_call(prompt, response_format="json", temperature=0.65)

        return EmailDraft(
            company_id=company.id or "",
            company_name=company.name,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=result["subject"],
            body_html=result.get("body_html", result["body_text"]),
            body_text=result["body_text"],
            cluster_id=company.cluster_id or 0,
            tone=profile.recommended_tone,
            personalization_notes=result.get("personalization_notes", ""),
        )

    def _build_hook_context(self, company: Company) -> str:
        """
        Construye el contexto de 'gancho' más relevante para esta empresa.
        Prioriza: datos de ventas visibles > sector con estacionalidad >
        crecimiento/problemas > tecnología usada.
        """
        hooks = []

        # Gancho por sector con estacionalidad conocida
        seasonal_sectors = {
            "retail": "El retail tiene picos claros de demanda (Black Friday, Navidad, rebajas). Predecir esos picos con datos propios puede marcar la diferencia en stock y márgenes.",
            "hostelería": "La hostelería tiene estacionalidad marcada (temporada alta, festivos, eventos locales). Anticipar la demanda permite ajustar personal, compras y carta.",
            "manufactura": "En manufactura, la planificación de producción depende de prever la demanda. Un error de predicción se traduce en sobrestock o rotura.",
            "logística": "En logística, la variabilidad de la demanda afecta directamente a flotas y rutas. Predecir volúmenes permite optimizar recursos.",
            "educación": "En formación, entender qué cursos crecen, cuáles decaen y cuándo se matriculan los alumnos permite planificar mejor la oferta.",
        }
        if company.sector and company.sector.value in seasonal_sectors:
            hooks.append(seasonal_sectors[company.sector.value])

        # Gancho por tecnología (Excel = oportunidad clara)
        tech_lower = [t.lower() for t in company.technologies_used]
        if any(t in tech_lower for t in ["excel", "hojas de cálculo", "google sheets"]):
            hooks.append("Usan Excel/hojas de cálculo para gestionar datos. Probablemente tienen información valiosa atrapada ahí que no están explotando.")
        if any(t in tech_lower for t in ["sap", "erp", "odoo", "dynamics"]):
            hooks.append("Tienen ERP, lo que significa que generan datos transaccionales ricos. Ideal para análisis de ventas cruzado con productos, clientes y zonas.")
        if any(t in tech_lower for t in ["shopify", "woocommerce", "prestashop", "magento"]):
            hooks.append("Tienen ecommerce, lo que significa datos de ventas online, carritos, conversión. Todo analizable para optimizar qué productos empujar y a quién.")

        # Gancho por tamaño
        if company.employee_count and company.employee_count < 50:
            hooks.append("Empresa pequeña: probablemente las decisiones de ventas se toman con intuición más que con datos. ARIGRA puede darles la capa analítica que una empresa grande tiene con su equipo de BI.")

        # Gancho por pain points identificados
        if company.pain_points:
            hooks.append(f"Pain points detectados: {', '.join(company.pain_points[:3])}. Conectar estos problemas con cómo los datos de ventas pueden ayudar a resolverlos.")

        # Gancho por productos/servicios (diversidad = análisis de portfolio)
        if len(company.products_services) >= 3:
            hooks.append(f"Tienen múltiples líneas de producto ({', '.join(company.products_services[:4])}). Análisis de portfolio: cuáles crecen, cuáles decaen, dónde poner foco.")

        if not hooks:
            hooks.append("Sin datos específicos suficientes. Usar un ángulo genérico de sector: la mayoría de empresas tienen datos de ventas que no están aprovechando.")

        return "\n".join(f"- {h}" for h in hooks)


# ─── Agente Sender ───────────────────────────────────────────

class SenderAgent(BaseAgent):
    """Envía emails con rate limiting y rotación de firmantes."""

    def __init__(self):
        super().__init__(
            name="Sender",
            description="Envío de emails con control de velocidad",
        )
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")

        self.max_per_day = int(os.getenv("MAX_EMAILS_PER_DAY", "50"))
        self.max_per_hour = int(os.getenv("MAX_EMAILS_PER_HOUR", "15"))
        self.delay_seconds = int(os.getenv("DELAY_BETWEEN_EMAILS_SEC", "30"))

        self._sent_today = 0
        self._sent_this_hour = 0

    async def execute(
        self,
        drafts: list[EmailDraft],
        dry_run: bool = True,
    ) -> list[EmailDraft]:
        """Envía los emails generados."""
        self.log_step(
            "Modo preview" if dry_run else "Enviando emails",
            f"{len(drafts)} emails"
        )

        sent_drafts = []
        for i, draft in enumerate(drafts):
            if self._sent_today >= self.max_per_day:
                self.logger.warning("Límite diario alcanzado")
                break
            if self._sent_this_hour >= self.max_per_hour:
                self.logger.info("Límite por hora, esperando...")
                await asyncio.sleep(60)
                self._sent_this_hour = 0

            if dry_run:
                self.log_step(f"[PREVIEW] Email {i+1}", f"→ {draft.recipient_email}")
                print(f"\n{'='*60}")
                print(f"Para: {draft.recipient_email} ({draft.company_name})")
                print(f"Asunto: {draft.subject}")
                print(f"Tono: {draft.tone.value} | Cluster: {draft.cluster_id}")
                print(f"{'─'*60}")
                print(draft.body_text)
                print(f"{'─'*60}")
                print(f"[Personalización: {draft.personalization_notes}]")
                print(f"{'='*60}\n")
                draft.sent = True
            else:
                success = await self._send_email(draft)
                if success:
                    draft.sent = True
                    draft.sent_at = datetime.now()
                    self._sent_today += 1
                    self._sent_this_hour += 1
                    sent_drafts.append(draft)
                    if i < len(drafts) - 1:
                        await asyncio.sleep(self.delay_seconds)

        self.log_step("Envío completado", f"{len(sent_drafts)} emails")
        return sent_drafts

    async def _send_email(self, draft: EmailDraft) -> bool:
        """Envía un email via SMTP."""
        try:
            sender_email = os.getenv("SENDER_EMAIL", self.smtp_user)
            sender_name = os.getenv("SENDER_NAME", "ARIGRA")

            msg = MIMEMultipart("alternative")
            msg["Subject"] = draft.subject
            msg["From"] = f"{sender_name} <{sender_email}>"
            msg["To"] = draft.recipient_email
            msg["Reply-To"] = sender_email

            msg.attach(MIMEText(draft.body_text, "plain", "utf-8"))
            msg.attach(MIMEText(draft.body_html, "html", "utf-8"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            self.log_step("Enviado", f"→ {draft.recipient_email}")
            return True

        except Exception as e:
            self.logger.error(f"Error enviando a {draft.recipient_email}: {e}")
            return False


# ─── Agente Follow-Up ────────────────────────────────────────

class FollowUpAgent(BaseAgent):
    """Seguimiento automático con estrategia progresiva adaptada a ARIGRA."""

    def __init__(self, follow_up_days: list[int] | None = None):
        super().__init__(
            name="Follow-Up ARIGRA",
            description="Seguimiento con aporte de valor progresivo",
        )
        self.follow_up_days = follow_up_days or [3, 7, 14]

    async def execute(
        self,
        drafts: list[EmailDraft],
        companies: list[Company],
    ) -> list[EmailDraft]:
        """Genera follow-ups para emails sin respuesta."""
        self.log_step("Evaluando follow-ups", f"{len(drafts)} emails previos")

        company_map = {c.id: c for c in companies if c.id}
        follow_ups: list[EmailDraft] = []

        for draft in drafts:
            if draft.replied or not draft.sent or not draft.sent_at:
                continue

            days_since = (datetime.now() - draft.sent_at).days
            follow_up_number = draft.follow_up_count + 1

            if follow_up_number > len(self.follow_up_days):
                continue
            if days_since < self.follow_up_days[follow_up_number - 1]:
                continue

            company = company_map.get(draft.company_id)
            if not company:
                continue

            try:
                follow_up = await self._generate_follow_up(draft, company, follow_up_number)
                follow_ups.append(follow_up)
            except Exception as e:
                self.logger.error(f"Error en follow-up para {draft.company_name}: {e}")

        self.log_step("Follow-ups listos", f"{len(follow_ups)} emails")
        return follow_ups

    async def _generate_follow_up(
        self,
        original: EmailDraft,
        company: Company,
        follow_up_number: int,
    ) -> EmailDraft:
        """Genera follow-up con estrategia progresiva."""

        strategies = {
            1: """ESTRATEGIA: Aportar valor sin pedir nada.
Compartir una observación concreta sobre su sector o tipo de negocio que demuestre
que ARIGRA entiende sus retos. Por ejemplo: "En [sector], las empresas que analizan
sus datos de ventas por zona descubren que el 20% de sus territorios genera el 60% del margen."
Cerrar con: "Si te interesa, encantado de contarte más." Sin presión.""",

            2: """ESTRATEGIA: Mini caso de uso relevante.
Describir en 2-3 frases un caso (real o realista) de una empresa similar:
qué problema tenían, qué hizo ARIGRA y qué resultado obtuvieron.
Cerrar preguntando si se encuentran en una situación parecida.""",

            3: """ESTRATEGIA: Cierre respetuoso.
Ser breve y directo: "Te escribí hace unas semanas sobre cómo los datos de ventas
pueden ayudar a [empresa]. Entiendo que igual no es el momento o no encaja.
Si prefieres que no te vuelva a escribir, dímelo sin problema.
Y si en algún momento os interesa, aquí estaremos." Fin. Dignidad ante todo.""",
        }

        prompt = f"""{ARIGRA_CONTEXT}

=== TAREA ===
Genera el follow-up #{follow_up_number} para un email que no obtuvo respuesta.

=== EMAIL ORIGINAL ===
Asunto: {original.subject}
Cuerpo (resumen): {original.body_text[:300]}

=== EMPRESA ===
{company.name} | Sector: {company.sector.value if company.sector else '?'} | {company.city or '?'}
Productos: {', '.join(company.products_services[:3]) if company.products_services else '?'}

=== ESTRATEGIA PARA ESTE FOLLOW-UP ===
{strategies.get(follow_up_number, strategies[3])}

=== REGLAS ===
1. Máximo 80 palabras
2. NO repetir el primer email
3. Asunto: "Re: [asunto original]"
4. Mantener el mismo tono que el email original
5. El follow-up 3 DEBE dar opción clara de no recibir más emails

Devuelve SOLO JSON:
{{
    "subject": "Re: {original.subject}",
    "body_text": "Texto del follow-up",
    "body_html": "HTML del follow-up"
}}"""

        result = await self.llm_call(prompt, response_format="json", temperature=0.5)

        return EmailDraft(
            company_id=original.company_id,
            company_name=original.company_name,
            recipient_email=original.recipient_email,
            recipient_name=original.recipient_name,
            subject=result["subject"],
            body_html=result.get("body_html", result["body_text"]),
            body_text=result["body_text"],
            cluster_id=original.cluster_id,
            tone=original.tone,
            follow_up_count=follow_up_number,
        )
