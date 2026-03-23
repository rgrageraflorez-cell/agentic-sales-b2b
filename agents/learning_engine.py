"""
LearningEngineAgent — Sistema de feedback loop que registra resultados y optimiza futuras campañas.
"""

from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from agents.base import BaseAgent
from models import Company, EmailDraft


class LearningEngineAgent(BaseAgent):
    """Motor de aprendizaje que analiza resultados y optimiza campañas."""

    def __init__(self, data_dir: str = "./data"):
        super().__init__(
            name="Motor de Aprendizaje",
            description="Analiza resultados de campañas y genera recomendaciones para optimizar",
        )
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.records_path = self.data_dir / "campaign_records.json"
        self.insights_path = self.data_dir / "learning_insights.json"
        self.records: list[dict] = self._load_records()

    def _load_records(self) -> list[dict]:
        """Carga registros históricos."""
        if self.records_path.exists():
            return json.loads(self.records_path.read_text(encoding="utf-8"))
        return []

    def _save_records(self):
        """Guarda registros."""
        self.records_path.write_text(
            json.dumps(self.records, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

    # ─── Registro de eventos ────────────────────────────────

    def register_send(self, company: Company, draft: EmailDraft):
        """Registra el envío de un email."""
        record = {
            "company_name": company.name,
            "company_id": company.id,
            "sector": company.sector.value if company.sector else "desconocido",
            "size": company.size.value if company.size else "desconocido",
            "cluster_id": company.cluster_id,
            "cluster_label": company.cluster_label,
            "tone": draft.tone.value,
            "subject": draft.subject,
            "arigra_angle": getattr(company, "_signals_data", {}).get("arigra_angle", ""),
            "pain_points_used": company.pain_points[:3] if company.pain_points else [],
            "lead_score": company.lead_score,
            "sent_at": datetime.now().isoformat(),
            "opened": False,
            "opened_at": None,
            "replied": False,
            "replied_at": None,
            "reply_sentiment": None,
            "meeting": False,
            "meeting_at": None,
            "converted": False,
            "converted_at": None,
        }
        self.records.append(record)
        self._save_records()

    def mark_opened(self, company_name: str) -> bool:
        """Marca un email como abierto."""
        for r in reversed(self.records):
            if r["company_name"].lower() == company_name.lower():
                r["opened"] = True
                r["opened_at"] = datetime.now().isoformat()
                self._save_records()
                return True
        return False

    def mark_replied(self, company_name: str, sentiment: str = "neutral") -> bool:
        """Marca una respuesta recibida."""
        for r in reversed(self.records):
            if r["company_name"].lower() == company_name.lower():
                r["replied"] = True
                r["replied_at"] = datetime.now().isoformat()
                r["reply_sentiment"] = sentiment
                self._save_records()
                return True
        return False

    def mark_meeting(self, company_name: str) -> bool:
        """Marca que se consiguió reunión."""
        for r in reversed(self.records):
            if r["company_name"].lower() == company_name.lower():
                r["meeting"] = True
                r["meeting_at"] = datetime.now().isoformat()
                self._save_records()
                return True
        return False

    def mark_converted(self, company_name: str) -> bool:
        """Marca conversión en cliente."""
        for r in reversed(self.records):
            if r["company_name"].lower() == company_name.lower():
                r["converted"] = True
                r["converted_at"] = datetime.now().isoformat()
                self._save_records()
                return True
        return False

    # ─── Análisis ───────────────────────────────────────────

    async def execute(self, **kwargs) -> dict:
        """Ejecuta el análisis completo y genera recomendaciones."""
        self.log_step("Analizando resultados", f"{len(self.records)} registros")

        if len(self.records) < 3:
            self.log_step("Datos insuficientes", "Mínimo 3 registros para analizar")
            return {"status": "insufficient_data", "records": len(self.records)}

        # Análisis por dimensión
        by_sector = self._analyze_by_dimension("sector")
        by_size = self._analyze_by_dimension("size")
        by_tone = self._analyze_by_dimension("tone")
        by_angle = self._analyze_by_dimension("arigra_angle")

        # Análisis de asuntos
        subjects = self._analyze_subjects()

        # Generar recomendaciones con LLM
        recommendations = await self._generate_recommendations(
            by_sector, by_size, by_tone, by_angle, subjects
        )

        insights = {
            "generated_at": datetime.now().isoformat(),
            "total_records": len(self.records),
            "analysis": {
                "by_sector": by_sector,
                "by_size": by_size,
                "by_tone": by_tone,
                "by_angle": by_angle,
                "subjects": subjects,
            },
            "recommendations": recommendations,
        }

        # Guardar insights
        self.insights_path.write_text(
            json.dumps(insights, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.log_step("Análisis completado", f"{len(recommendations)} recomendaciones")
        return insights

    def _analyze_by_dimension(self, dimension: str) -> dict:
        """Calcula métricas agrupadas por una dimensión."""
        groups: dict[str, list[dict]] = {}
        for r in self.records:
            key = r.get(dimension, "desconocido")
            if not key:
                key = "desconocido"
            groups.setdefault(key, []).append(r)

        results = {}
        for key, records in groups.items():
            total = len(records)
            opened = sum(1 for r in records if r.get("opened"))
            replied = sum(1 for r in records if r.get("replied"))
            meetings = sum(1 for r in records if r.get("meeting"))
            converted = sum(1 for r in records if r.get("converted"))

            results[key] = {
                "total": total,
                "open_rate": round(opened / total * 100, 1) if total else 0,
                "reply_rate": round(replied / total * 100, 1) if total else 0,
                "meeting_rate": round(meetings / total * 100, 1) if total else 0,
                "conversion_rate": round(converted / total * 100, 1) if total else 0,
            }

        return results

    def _analyze_subjects(self) -> list[dict]:
        """Analiza qué asuntos tienen mejor rendimiento."""
        subject_stats: dict[str, dict] = {}
        for r in self.records:
            subj = r.get("subject", "")
            if subj not in subject_stats:
                subject_stats[subj] = {"total": 0, "opened": 0, "replied": 0}
            subject_stats[subj]["total"] += 1
            if r.get("opened"):
                subject_stats[subj]["opened"] += 1
            if r.get("replied"):
                subject_stats[subj]["replied"] += 1

        results = []
        for subj, stats in subject_stats.items():
            results.append({
                "subject": subj,
                "total": stats["total"],
                "open_rate": round(stats["opened"] / stats["total"] * 100, 1),
                "reply_rate": round(stats["replied"] / stats["total"] * 100, 1),
            })

        return sorted(results, key=lambda x: x["reply_rate"], reverse=True)

    async def _generate_recommendations(
        self,
        by_sector: dict,
        by_size: dict,
        by_tone: dict,
        by_angle: dict,
        subjects: list[dict],
    ) -> list[str]:
        """Genera recomendaciones accionables con LLM."""
        prompt = f"""Analiza estos resultados de campañas de email B2B y genera 5-8 recomendaciones
CONCRETAS y accionables para mejorar la siguiente campaña.

RESULTADOS POR SECTOR:
{json.dumps(by_sector, indent=2, ensure_ascii=False)}

RESULTADOS POR TAMAÑO:
{json.dumps(by_size, indent=2, ensure_ascii=False)}

RESULTADOS POR TONO:
{json.dumps(by_tone, indent=2, ensure_ascii=False)}

RESULTADOS POR ÁNGULO ARIGRA:
{json.dumps(by_angle, indent=2, ensure_ascii=False)}

MEJORES ASUNTOS:
{json.dumps(subjects[:10], indent=2, ensure_ascii=False)}

Contexto: ARIGRA vende análisis de datos de ventas, predicción de demanda y dashboards a empresas.

Devuelve SOLO un JSON array con 5-8 recomendaciones. Cada recomendación debe ser una frase
concreta y accionable. Ejemplo: "Priorizar sector retail (reply rate 12%). Subir peso en scoring."

Devuelve SOLO JSON:
["recomendación 1", "recomendación 2", ...]"""

        try:
            result = await self.llm_call(prompt, response_format="json", temperature=0.4)
            return result if isinstance(result, list) else []
        except Exception as e:
            self.logger.warning(f"Error generando recomendaciones: {e}")
            return ["No se pudieron generar recomendaciones automáticas. Revisar datos manualmente."]

    # ─── Optimización activa (usado por otros agentes) ──────

    def get_sector_boost(self, sector: str) -> float:
        """Devuelve bonus/penalización al scoring basado en reply_rate del sector."""
        by_sector = self._analyze_by_dimension("sector")
        stats = by_sector.get(sector, {})

        if stats.get("total", 0) < 5:
            return 0  # Muestra insuficiente

        reply_rate = stats.get("reply_rate", 0)
        if reply_rate > 10:
            return 15  # Boost
        elif reply_rate < 3:
            return -10  # Penalización
        return 0

    def get_best_tone(self) -> str | None:
        """Devuelve el tono con mejor reply_rate."""
        by_tone = self._analyze_by_dimension("tone")
        if not by_tone:
            return None

        best = max(by_tone.items(), key=lambda x: x[1].get("reply_rate", 0))
        if best[1].get("total", 0) >= 3:
            return best[0]
        return None

    def get_best_angle(self) -> str | None:
        """Devuelve el ángulo ARIGRA con mejor resultado."""
        by_angle = self._analyze_by_dimension("arigra_angle")
        if not by_angle:
            return None

        # Filtrar los que tienen suficientes datos
        valid = {k: v for k, v in by_angle.items() if v.get("total", 0) >= 3 and k}
        if not valid:
            return None

        best = max(valid.items(), key=lambda x: x[1].get("reply_rate", 0))
        return best[0]
