"""
RolePersonalizerAgent — Detecta el rol del contacto y adapta la estrategia de comunicación.
"""

from __future__ import annotations
from typing import Any

from agents.base import BaseAgent
from models import Company, CompanySize


# ─── Estrategias por rol ────────────────────────────────────

ROLE_STRATEGIES = {
    "ceo": {
        "titles": [
            "ceo", "fundador", "cofundador", "co-fundador", "director general",
            "gerente", "propietario", "dueño", "socio director", "administrador",
        ],
        "tone": "directo",
        "focus": "crecimiento, rentabilidad, visión estratégica",
        "talk_about": [
            "Cómo los datos pueden impulsar decisiones de crecimiento",
            "Visibilidad sobre qué líneas de negocio son más rentables",
            "Anticiparse al mercado con predicciones basadas en datos propios",
        ],
        "avoid": [
            "Jerga técnica (no hablar de modelos, algoritmos ni metodología)",
            "Detalles de implementación",
            "Hablar de herramientas o tecnología específica",
        ],
        "cta": "15 minutos para enseñarte qué se puede sacar de vuestros datos de ventas",
        "email_style": {
            "max_words": 80,
            "approach": "Ir al grano. Resultado > proceso. Visión > detalle.",
        },
    },
    "comercial": {
        "titles": [
            "director comercial", "jefe de ventas", "responsable comercial",
            "director de ventas", "head of sales", "sales manager",
            "responsable de negocio", "business development",
        ],
        "tone": "cercano",
        "focus": "previsión de ventas, oportunidades comerciales, rendimiento del equipo",
        "talk_about": [
            "Prever qué va a vender tu equipo el próximo trimestre",
            "Detectar oportunidades de cross-sell y up-sell en tu cartera",
            "Saber qué clientes están en riesgo de irse antes de que se vayan",
        ],
        "avoid": [
            "Hablar en abstracto — siempre conectar con su día a día",
            "Sonar como consultor estratégico — sonar como alguien que entiende ventas",
            "Proponer análisis que no tengan impacto directo en revenue",
        ],
        "cta": "15 min para ver qué patrones esconden vuestros datos de ventas",
        "email_style": {
            "max_words": 110,
            "approach": "Hablar de 'tu equipo', 'tus clientes'. Cercano y práctico.",
        },
    },
    "operaciones": {
        "titles": [
            "director de operaciones", "coo", "jefe de operaciones",
            "responsable de logística", "supply chain", "director de producción",
            "operations manager", "jefe de almacén",
        ],
        "tone": "directo",
        "focus": "planificación, stock, eficiencia operativa, previsión de demanda",
        "talk_about": [
            "Reducir roturas de stock y sobrestock con predicción de demanda",
            "Planificar producción o compras con datos, no con intuición",
            "Optimizar recursos basándose en patrones reales de demanda",
        ],
        "avoid": [
            "Rodeos — ir directo al problema y la solución",
            "Hablar de estrategia o visión — hablar de eficiencia",
            "Promesas vagas — ser concreto en qué se va a mejorar",
        ],
        "cta": "15 min para ver cómo mejorar la planificación con vuestros datos",
        "email_style": {
            "max_words": 100,
            "approach": "Práctico, sin rodeos. Problema → dato → solución.",
        },
    },
    "marketing": {
        "titles": [
            "director de marketing", "cmo", "responsable de marketing",
            "head of marketing", "marketing manager", "brand manager",
            "digital marketing", "growth",
        ],
        "tone": "consultivo",
        "focus": "segmentación de clientes, campañas, comportamiento de compra",
        "talk_about": [
            "Entender qué segmentos de clientes son más rentables",
            "Medir el impacto real de las campañas en ventas",
            "Descubrir patrones de compra para personalizar ofertas",
        ],
        "avoid": [
            "Hablar solo de ventas brutas — hablar de comportamiento",
            "Ignorar el componente creativo — reconocer que los datos complementan",
            "Ser demasiado técnico — hacer preguntas que provoquen reflexión",
        ],
        "cta": "¿Hacemos una llamada de 15 min? Me gustaría entender cómo medís el impacto de vuestras campañas",
        "email_style": {
            "max_words": 115,
            "approach": "Empezar con pregunta. Consultivo. Datos + creatividad.",
        },
    },
    "datos": {
        "titles": [
            "data analyst", "data scientist", "business intelligence",
            "bi manager", "chief data officer", "cdo", "head of data",
            "analista de datos", "responsable de bi",
        ],
        "tone": "consultivo",
        "focus": "metodología, modelos, infraestructura de datos",
        "talk_about": [
            "Qué modelos usamos y por qué elegimos uno u otro según el caso",
            "Cómo integramos con las fuentes de datos que ya tienen",
            "Colaboración: complementamos su equipo, no lo reemplazamos",
        ],
        "avoid": [
            "Simplificar demasiado — este perfil valora el rigor",
            "Sonar como si vendiéramos una caja negra mágica",
            "Ignorar que ya tienen conocimientos — posicionarse como par",
        ],
        "cta": "¿Hablamos 15 min sobre metodología? Me interesa saber qué enfoque usáis",
        "email_style": {
            "max_words": 130,
            "approach": "Técnico pero no pedante. Par a par. Hablar de metodología.",
        },
    },
}

# Prioridad de roles para contactar (de más a menos preferido)
ROLE_PRIORITY = ["comercial", "ceo", "marketing", "operaciones", "datos"]


class RolePersonalizerAgent(BaseAgent):
    """Detecta el rol del contacto y adapta la estrategia de comunicación."""

    def __init__(self):
        super().__init__(
            name="Personalizador por Rol",
            description="Adapta tono, foco y estilo según el rol del destinatario",
        )

    async def execute(self, companies: list[Company]) -> list[Company]:
        """Personaliza la estrategia para cada empresa según el contacto."""
        self.log_step("Personalizando por rol", f"{len(companies)} empresas")

        for i, company in enumerate(companies):
            self.log_step(f"Analizando rol {i+1}/{len(companies)}", company.name)
            try:
                strategy = self._determine_strategy(company)
                company._role_strategy = strategy
            except Exception as e:
                self.logger.warning(f"Error personalizando {company.name}: {e}")
                company._role_strategy = self._default_strategy(company)

        self.log_step("Personalización completada")
        return companies

    def _determine_strategy(self, company: Company) -> dict:
        """Determina la mejor estrategia basada en el contacto disponible."""

        # Si hay contactos, clasificar cada uno y elegir el mejor
        if company.contacts:
            best_contact = None
            best_role_key = None
            best_priority = len(ROLE_PRIORITY)

            for contact in company.contacts:
                role_key = self._classify_role(contact.role)
                if role_key:
                    priority = ROLE_PRIORITY.index(role_key) if role_key in ROLE_PRIORITY else len(ROLE_PRIORITY)
                    if priority < best_priority:
                        best_priority = priority
                        best_contact = contact
                        best_role_key = role_key

            if best_role_key and best_contact:
                strategy = ROLE_STRATEGIES[best_role_key].copy()
                strategy["detected_role"] = best_role_key
                strategy["contact_name"] = best_contact.name
                strategy["contact_email"] = best_contact.email
                strategy["contact_title"] = best_contact.role
                return strategy

        # Si no hay contactos, usar el best_contact_role del diagnóstico
        if hasattr(company, "_diagnostic") and company._diagnostic:
            diag = company._diagnostic
            best_role = diag.get("best_contact_role", {})
            if best_role and best_role.get("role"):
                role_key = self._classify_role(best_role["role"])
                if role_key:
                    strategy = ROLE_STRATEGIES[role_key].copy()
                    strategy["detected_role"] = role_key
                    strategy["contact_name"] = ""
                    strategy["contact_email"] = company.email
                    strategy["contact_title"] = best_role["role"]
                    return strategy

        # Default según tamaño
        return self._default_strategy(company)

    def _default_strategy(self, company: Company) -> dict:
        """Estrategia por defecto según tamaño de empresa."""
        if company.size in (CompanySize.MICRO, CompanySize.SMALL):
            role_key = "ceo"
        else:
            role_key = "comercial"

        strategy = ROLE_STRATEGIES[role_key].copy()
        strategy["detected_role"] = role_key
        strategy["contact_name"] = ""
        strategy["contact_email"] = company.email
        strategy["contact_title"] = ""
        return strategy

    def _classify_role(self, role_title: str) -> str | None:
        """Clasifica un título de rol en una de las categorías."""
        if not role_title:
            return None

        role_lower = role_title.lower().strip()

        for role_key, config in ROLE_STRATEGIES.items():
            for title in config["titles"]:
                if title in role_lower:
                    return role_key

        return None
