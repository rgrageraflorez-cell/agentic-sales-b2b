"""
Orquestador Central v2 — coordina las 4 fases del pipeline de captación.
Incluye: PainPointDetector, PreDiagnostic, RolePersonalizer, LearningEngine.
"""

from __future__ import annotations
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from models import (
    ClusterProfile, Company, CompanySize, EmailDraft,
    LeadStatus, PipelineMetrics, Sector,
)
from agents.phase1_collection import ScraperAgent, EnricherAgent, ValidatorAgent
from agents.pain_point_detector import PainPointDetectorAgent
from agents.phase2_clustering import ClassifierAgent, ScorerAgent, SegmenterAgent
from agents.pre_diagnostic import PreDiagnosticAgent
from agents.role_personalizer import RolePersonalizerAgent
from agents.phase3_outreach import CopywriterAgent, SenderAgent, FollowUpAgent
from agents.humanizer import HumanizerAgent
from agents.learning_engine import LearningEngineAgent

load_dotenv()


class Orchestrator:
    """
    Orquestador central del sistema de captación v2.
    Coordina 13 agentes en 4 fases secuenciales.
    """

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Fase 1: Recolección
        self.scraper = ScraperAgent()
        self.enricher = EnricherAgent()
        self.validator = ValidatorAgent()

        # Fase 2: Inteligencia
        self.pain_detector = PainPointDetectorAgent()
        self.classifier = ClassifierAgent()
        self.scorer = ScorerAgent()
        self.segmenter = SegmenterAgent()

        # Fase 3: Outreach
        self.pre_diagnostic = PreDiagnosticAgent(
            diagnostics_dir=str(self.data_dir / "diagnostics")
        )
        self.role_personalizer = RolePersonalizerAgent()
        self.copywriter = CopywriterAgent()
        self.humanizer = HumanizerAgent()
        self.sender = SenderAgent()
        self.follow_up = FollowUpAgent()

        # Fase 4: Aprendizaje
        self.learning_engine = LearningEngineAgent(data_dir=str(self.data_dir))

        # Estado
        self.companies: list[Company] = []
        self.cluster_profiles: list[ClusterProfile] = []
        self.email_drafts: list[EmailDraft] = []
        self.metrics = PipelineMetrics()

        logger.info("Orquestador v2 inicializado con 14 agentes")

    # ─── Fase 1: Recolección ─────────────────────────────────

    async def run_phase_1(
        self,
        query: str = "empresas tecnología Madrid",
        sources: list[str] | None = None,
        max_results: int = 100,
    ) -> list[Company]:
        """
        Fase 1: Scraping → Enriquecimiento → Validación
        """
        logger.info("═══ FASE 1: RECOLECCIÓN DE DATOS ═══")
        logger.info(f"Query: '{query}' | Fuentes: {sources} | Max: {max_results}")

        # 1.1 Scraping
        raw_companies = await self.scraper.execute(
            query=query, sources=sources, max_results=max_results
        )
        self.metrics.total_scraped = len(raw_companies)

        # 1.2 Enriquecimiento
        enriched = await self.enricher.execute(raw_companies)
        self.metrics.total_enriched = len(enriched)

        # 1.3 Validación
        validated = await self.validator.execute(enriched)
        self.metrics.total_validated = len(validated)

        self.companies = validated
        self._save_state("phase1_companies.json")

        logger.info(
            f"Fase 1 completada: {self.metrics.total_scraped} scrapeadas → "
            f"{self.metrics.total_enriched} enriquecidas → "
            f"{self.metrics.total_validated} validadas"
        )
        return self.companies

    # ─── Fase 2: Inteligencia ────────────────────────────────

    async def run_phase_2(
        self,
        n_clusters: int = 5,
        ideal_sizes: list[CompanySize] | None = None,
        ideal_sectors: list[Sector] | None = None,
    ) -> tuple[list[Company], list[ClusterProfile]]:
        """
        Fase 2: Pain Points → Clasificación → Scoring (con aprendizaje) → Segmentación
        """
        logger.info("═══ FASE 2: INTELIGENCIA ═══")

        if not self.companies:
            self._load_state("phase1_companies.json")

        # 2.1 Detección de pain points reales
        self.companies = await self.pain_detector.execute(self.companies)

        # 2.2 Clasificación
        classified = await self.classifier.execute(self.companies)

        # 2.3 Scoring (con boost del learning engine)
        scored = await self.scorer.execute(
            classified,
            ideal_sizes=ideal_sizes,
            ideal_sectors=ideal_sectors,
        )

        # Aplicar boost del learning engine
        for company in scored:
            if company.sector:
                boost = self.learning_engine.get_sector_boost(company.sector.value)
                if boost:
                    company.lead_score = min(100, max(0, company.lead_score + boost))

        # 2.4 Segmentación
        self.segmenter.n_clusters = n_clusters
        clustered, profiles = await self.segmenter.execute(scored)

        self.companies = clustered
        self.cluster_profiles = profiles
        self.metrics.total_clustered = len(clustered)
        self.metrics.clusters = profiles

        self._save_state("phase2_companies.json")
        self._save_profiles("phase2_profiles.json")

        logger.info(f"Fase 2 completada: {len(profiles)} clusters creados")
        for p in profiles:
            logger.info(f"  Cluster {p.cluster_id}: '{p.label}' ({p.company_count} empresas, score medio: {p.avg_score})")

        return self.companies, self.cluster_profiles

    # ─── Fase 3: Outreach ────────────────────────────────────

    async def run_phase_3(
        self,
        dry_run: bool = True,
    ) -> list[EmailDraft]:
        """
        Fase 3: PreDiagnóstico → Personalización por Rol → Copywriting → Envío
        """
        logger.info(f"═══ FASE 3: OUTREACH PERSONALIZADO ═══ ({'DRY RUN' if dry_run else 'LIVE'})")

        if not self.companies:
            self._load_state("phase2_companies.json")
        if not self.cluster_profiles:
            self._load_profiles("phase2_profiles.json")

        # 3.1 Pre-diagnóstico (dossier comercial)
        self.companies = await self.pre_diagnostic.execute(self.companies)

        # 3.2 Personalización por rol
        self.companies = await self.role_personalizer.execute(self.companies)

        # 3.3 Generar emails
        drafts = await self.copywriter.execute(self.companies, self.cluster_profiles)

        # 3.4 Humanizar (eliminar patrones de escritura IA)
        drafts = await self.humanizer.execute(drafts)

        # 3.5 Enviar
        sent = await self.sender.execute(drafts, dry_run=dry_run)
        self.metrics.total_emails_sent = len(sent)

        # Actualizar status y registrar en learning engine
        sent_ids = {d.company_id for d in sent if d.sent}
        company_map = {c.id: c for c in self.companies if c.id}
        for d in sent:
            if d.sent and d.company_id in company_map:
                company = company_map[d.company_id]
                company.status = LeadStatus.EMAIL_SENT
                if not dry_run:
                    self.learning_engine.register_send(company, d)

        self.email_drafts = drafts
        self._save_state("phase3_companies.json")
        self._save_drafts("phase3_drafts.json")

        logger.info(f"Fase 3 completada: {len(sent)} emails {'previsualizados' if dry_run else 'enviados'}")
        return drafts

    # ─── Follow-ups ──────────────────────────────────────────

    async def run_follow_ups(self, dry_run: bool = True) -> list[EmailDraft]:
        """Ejecuta el ciclo de follow-ups."""
        logger.info("═══ FOLLOW-UPS ═══")

        if not self.email_drafts:
            self._load_drafts("phase3_drafts.json")

        follow_ups = await self.follow_up.execute(self.email_drafts, self.companies)

        if follow_ups:
            sent = await self.sender.execute(follow_ups, dry_run=dry_run)
            logger.info(f"{len(sent)} follow-ups {'previsualizados' if dry_run else 'enviados'}")

        return follow_ups

    # ─── Fase 4: Aprendizaje ─────────────────────────────────

    async def run_phase_4(self) -> dict:
        """Fase 4: Análisis de resultados y generación de insights."""
        logger.info("═══ FASE 4: APRENDIZAJE ═══")
        insights = await self.learning_engine.execute()
        return insights

    # ─── Feedback (usado desde CLI) ──────────────────────────

    def mark_opened(self, company_name: str):
        """Registra apertura de email."""
        if self.learning_engine.mark_opened(company_name):
            logger.info(f"✓ Apertura registrada: {company_name}")
        else:
            logger.warning(f"Empresa no encontrada: {company_name}")

    def mark_replied(self, company_name: str, sentiment: str = "neutral"):
        """Registra respuesta recibida."""
        if self.learning_engine.mark_replied(company_name, sentiment):
            logger.info(f"✓ Respuesta registrada: {company_name} (sentimiento: {sentiment})")
        else:
            logger.warning(f"Empresa no encontrada: {company_name}")

    def mark_meeting(self, company_name: str):
        """Registra reunión conseguida."""
        if self.learning_engine.mark_meeting(company_name):
            logger.info(f"✓ Reunión registrada: {company_name}")
        else:
            logger.warning(f"Empresa no encontrada: {company_name}")

    def mark_converted(self, company_name: str):
        """Registra conversión en cliente."""
        if self.learning_engine.mark_converted(company_name):
            logger.info(f"✓ Conversión registrada: {company_name}")
        else:
            logger.warning(f"Empresa no encontrada: {company_name}")

    # ─── Pipeline completo ───────────────────────────────────

    async def run_full_pipeline(
        self,
        query: str = "empresas tecnología Madrid",
        sources: list[str] | None = None,
        max_results: int = 100,
        n_clusters: int = 5,
        dry_run: bool = True,
    ) -> PipelineMetrics:
        """Ejecuta el pipeline completo de principio a fin."""
        logger.info("╔══════════════════════════════════════╗")
        logger.info("║  PIPELINE DE CAPTACIÓN v2 - INICIO   ║")
        logger.info("╚══════════════════════════════════════╝")

        await self.run_phase_1(query=query, sources=sources, max_results=max_results)
        await self.run_phase_2(n_clusters=n_clusters)
        await self.run_phase_3(dry_run=dry_run)

        self._print_metrics()
        return self.metrics

    # ─── Persistencia ────────────────────────────────────────

    def _save_state(self, filename: str):
        """Guarda el estado de las empresas."""
        path = self.data_dir / filename
        data = [c.model_dump(mode="json") for c in self.companies]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        logger.debug(f"Estado guardado: {path}")

    def _load_state(self, filename: str):
        """Carga el estado de las empresas."""
        path = self.data_dir / filename
        if path.exists():
            data = json.loads(path.read_text())
            self.companies = [Company(**d) for d in data]
            logger.debug(f"Estado cargado: {len(self.companies)} empresas desde {path}")

    def _save_profiles(self, filename: str):
        """Guarda perfiles de cluster."""
        path = self.data_dir / filename
        data = [p.model_dump(mode="json") for p in self.cluster_profiles]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def _load_profiles(self, filename: str):
        """Carga perfiles de cluster."""
        path = self.data_dir / filename
        if path.exists():
            data = json.loads(path.read_text())
            self.cluster_profiles = [ClusterProfile(**d) for d in data]

    def _save_drafts(self, filename: str):
        """Guarda borradores de email."""
        path = self.data_dir / filename
        data = [d.model_dump(mode="json") for d in self.email_drafts]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str))

    def _load_drafts(self, filename: str):
        """Carga borradores de email."""
        path = self.data_dir / filename
        if path.exists():
            data = json.loads(path.read_text())
            self.email_drafts = [EmailDraft(**d) for d in data]

    def _print_metrics(self):
        """Imprime métricas del pipeline."""
        m = self.metrics
        logger.info("╔══════════════════════════════════════╗")
        logger.info("║       MÉTRICAS DEL PIPELINE v2       ║")
        logger.info("╠══════════════════════════════════════╣")
        logger.info(f"║  Scrapeadas:    {m.total_scraped:>6}              ║")
        logger.info(f"║  Enriquecidas:  {m.total_enriched:>6}              ║")
        logger.info(f"║  Validadas:     {m.total_validated:>6}              ║")
        logger.info(f"║  Clusterizadas: {m.total_clustered:>6}              ║")
        logger.info(f"║  Emails enviados:{m.total_emails_sent:>5}              ║")
        logger.info("╚══════════════════════════════════════╝")


# ─── CLI ─────────────────────────────────────────────────────

async def main():
    """Punto de entrada principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Sistema Agéntico de Captación B2B v2")
    parser.add_argument("--query", default="empresas tecnología Madrid")
    parser.add_argument("--sources", nargs="+", default=["google_maps", "web_directories"])
    parser.add_argument("--max-results", type=int, default=100)
    parser.add_argument("--clusters", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--live", action="store_true", help="Enviar emails reales")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4], help="Ejecutar solo una fase")

    # Feedback
    parser.add_argument("--mark-opened", type=str, help="Registrar apertura de email")
    parser.add_argument("--mark-reply", type=str, help="Registrar respuesta")
    parser.add_argument("--mark-meeting", type=str, help="Registrar reunión")
    parser.add_argument("--mark-converted", type=str, help="Registrar conversión")
    parser.add_argument("--sentiment", default="neutral", choices=["positive", "neutral", "negative"])
    parser.add_argument("--insights", action="store_true", help="Generar insights de aprendizaje")

    args = parser.parse_args()
    orch = Orchestrator()

    # Comandos de feedback
    if args.mark_opened:
        orch.mark_opened(args.mark_opened)
        return
    if args.mark_reply:
        orch.mark_replied(args.mark_reply, args.sentiment)
        return
    if args.mark_meeting:
        orch.mark_meeting(args.mark_meeting)
        return
    if args.mark_converted:
        orch.mark_converted(args.mark_converted)
        return
    if args.insights:
        insights = await orch.run_phase_4()
        if insights.get("recommendations"):
            print("\n📊 Recomendaciones del Learning Engine:")
            for i, rec in enumerate(insights["recommendations"], 1):
                print(f"  {i}. {rec}")
        return

    # Pipeline
    if args.phase == 1:
        await orch.run_phase_1(query=args.query, sources=args.sources, max_results=args.max_results)
    elif args.phase == 2:
        await orch.run_phase_2(n_clusters=args.clusters)
    elif args.phase == 3:
        await orch.run_phase_3(dry_run=not args.live)
    elif args.phase == 4:
        await orch.run_phase_4()
    else:
        await orch.run_full_pipeline(
            query=args.query,
            sources=args.sources,
            max_results=args.max_results,
            n_clusters=args.clusters,
            dry_run=not args.live,
        )


if __name__ == "__main__":
    asyncio.run(main())
