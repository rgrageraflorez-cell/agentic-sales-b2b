"""
PreDiagnosticAgent — Genera un dossier comercial interno ANTES de redactar el email.
Doble utilidad: mejora el email Y prepara a Hugo/Rodrigo para la reunión.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from agents.base import BaseAgent
from models import Company


class PreDiagnosticAgent(BaseAgent):
    """Genera un dossier comercial completo para cada empresa."""

    def __init__(self, diagnostics_dir: str = "./data/diagnostics"):
        super().__init__(
            name="Pre-Diagnóstico",
            description="Genera dossier comercial interno con argumento, objeciones y estrategia",
        )
        self.diagnostics_dir = Path(diagnostics_dir)
        self.diagnostics_dir.mkdir(parents=True, exist_ok=True)

    async def execute(self, companies: list[Company]) -> list[Company]:
        """Genera diagnóstico para cada empresa."""
        self.log_step("Generando diagnósticos", f"{len(companies)} empresas")

        for i, company in enumerate(companies):
            self.log_step(f"Diagnosticando {i+1}/{len(companies)}", company.name)
            try:
                diagnostic = await self._generate_diagnostic(company)
                company._diagnostic = diagnostic

                # Guardar dossier individual
                diag_path = self.diagnostics_dir / f"{company.id}_diag.json"
                diag_path.write_text(
                    json.dumps(diagnostic, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

            except Exception as e:
                self.logger.warning(f"Error en diagnóstico de {company.name}: {e}")
                company._diagnostic = {}

        self.log_step("Diagnósticos completados")
        return companies

    async def _generate_diagnostic(self, company: Company) -> dict:
        """Genera el dossier comercial usando LLM."""
        signals_info = ""
        if hasattr(company, "_signals_data") and company._signals_data:
            signals = company._signals_data
            signals_info = f"""
SEÑALES DETECTADAS:
- Señales encontradas: {len(signals.get('signals_found', []))}
- Peso total: {signals.get('total_weight', 0)}
- Ángulo ARIGRA sugerido: {signals.get('arigra_angle', 'no definido')}
- Hook de apertura: {signals.get('opening_hook', 'no definido')}
- Signal score: {signals.get('signal_score', 0)}/100
"""

        prompt = f"""Genera un dossier comercial INTERNO para preparar la venta a esta empresa.
Este documento NO se envía al cliente — es para que Hugo y Rodrigo estén preparados.

=== EMPRESA ===
Nombre: {company.name}
Sector: {company.sector.value if company.sector else 'desconocido'}
Tamaño: {company.size.value if company.size else 'desconocido'} ({company.employee_count or '?'} empleados)
Ciudad: {company.city or 'desconocida'}
Web: {company.website or 'no disponible'}
Productos/servicios: {', '.join(company.products_services[:6]) if company.products_services else 'desconocidos'}
Tecnologías: {', '.join(company.technologies_used[:5]) if company.technologies_used else 'desconocidas'}
Pain points: {', '.join(company.pain_points[:4]) if company.pain_points else 'no identificados'}
Lead score: {company.lead_score}/100
Contactos: {', '.join(f"{c.role} ({c.name})" for c in company.contacts[:3]) if company.contacts else 'no identificados'}
{signals_info}

=== SERVICIOS ARIGRA ===
1. Análisis de ventas (evolución, productos, marcas, zonas, clientes)
2. Predicción de demanda (series temporales, regresión, curvas de adopción)
3. Dashboards y visualización (informes claros para dirección/ventas/marketing)

Devuelve SOLO JSON con este formato exacto:
{{
    "company_summary": "Resumen ejecutivo de 2-3 frases",
    "why_they_fit": "Por qué encaja como cliente de ARIGRA (específico, no genérico)",
    "predicted_needs": [
        "Necesidad 1 conectada con señales reales",
        "Necesidad 2",
        "Necesidad 3"
    ],
    "best_arigra_service": {{
        "service": "Nombre del servicio más vendible",
        "reason": "Por qué este y no otro",
        "one_liner": "Pitch en una frase"
    }},
    "secondary_service": {{
        "service": "Servicio de upsell natural",
        "reason": "Por qué encaja como siguiente paso"
    }},
    "commercial_argument": "El argumento comercial principal — concreto, basado en datos/señales, no genérico",
    "expected_objections": [
        {{
            "objection": "Objeción probable 1",
            "counter": "Contraargumento"
        }},
        {{
            "objection": "Objeción probable 2",
            "counter": "Contraargumento"
        }}
    ],
    "best_contact_role": {{
        "role": "CEO / Director Comercial / etc.",
        "why": "Por qué este rol es el mejor punto de entrada"
    }},
    "email_tone_recommendation": "formal|cercano|directo|consultivo",
    "email_angle": "Propuesta concreta para el ángulo del email",
    "meeting_talking_points": [
        "Tema 1 para la reunión si responde",
        "Tema 2",
        "Tema 3"
    ],
    "risk_level": {{
        "level": "bajo|medio|alto",
        "reason": "Por qué este nivel de riesgo"
    }},
    "priority": {{
        "level": "alta|media|baja",
        "reason": "Justificación de la prioridad"
    }}
}}"""

        result = await self.llm_call(prompt, response_format="json", temperature=0.3)
        return result
