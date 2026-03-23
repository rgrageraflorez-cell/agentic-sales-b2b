"""
Ejemplo de uso del sistema agéntico de captación.
Ejecutar: python example_usage.py
"""

import asyncio
from agents.orchestrator import Orchestrator
from models import Company, CompanySize, Sector, LeadStatus


async def demo_with_sample_data():
    """
    Demo usando datos de ejemplo para mostrar el pipeline completo
    sin necesidad de APIs externas.
    """
    print("\n🚀 Demo del Sistema Agéntico de Captación B2B\n")

    # ─── Crear datos de ejemplo ──────────────────────────────
    sample_companies = [
        Company(
            id="demo_001",
            name="TechSolutions Madrid",
            domain="techsolutions.es",
            website="https://techsolutions.es",
            email="info@techsolutions.es",
            city="Madrid",
            sector=Sector.TECH,
            size=CompanySize.SMALL,
            employee_count=25,
            products_services=["desarrollo web", "apps móviles", "consultoría IT"],
            technologies_used=["Python", "React", "AWS"],
            description="Empresa de desarrollo de software a medida",
            pain_points=["necesitan automatización", "crecimiento rápido"],
            status=LeadStatus.VALIDATED,
        ),
        Company(
            id="demo_002",
            name="Retail Innovation SL",
            domain="retailinnovation.com",
            website="https://retailinnovation.com",
            email="contacto@retailinnovation.com",
            city="Barcelona",
            sector=Sector.RETAIL,
            size=CompanySize.MEDIUM,
            employee_count=120,
            products_services=["ecommerce", "punto de venta", "gestión de inventario"],
            technologies_used=["Shopify", "SAP"],
            description="Cadena de tiendas con presencia online en crecimiento",
            pain_points=["integración omnicanal", "automatización logística"],
            status=LeadStatus.VALIDATED,
        ),
        Company(
            id="demo_003",
            name="FinData Analytics",
            domain="findata.es",
            website="https://findata.es",
            email="hello@findata.es",
            city="Valencia",
            sector=Sector.FINANCE,
            size=CompanySize.SMALL,
            employee_count=15,
            products_services=["análisis de datos", "reporting financiero", "dashboards"],
            technologies_used=["Python", "Tableau", "PostgreSQL"],
            description="Startup de análisis financiero para pymes",
            pain_points=["escalar infraestructura", "seguridad de datos"],
            status=LeadStatus.VALIDATED,
        ),
        Company(
            id="demo_004",
            name="EduTech Academy",
            domain="edutechacademy.es",
            website="https://edutechacademy.es",
            email="admin@edutechacademy.es",
            city="Sevilla",
            sector=Sector.EDUCATION,
            size=CompanySize.MICRO,
            employee_count=8,
            products_services=["formación online", "plataforma LMS", "cursos tech"],
            technologies_used=["Moodle", "WordPress"],
            description="Academia de formación tecnológica online",
            pain_points=["plataforma anticuada", "falta de automatización"],
            status=LeadStatus.VALIDATED,
        ),
        Company(
            id="demo_005",
            name="LogiTransport Express",
            domain="logitransport.es",
            website="https://logitransport.es",
            email="operaciones@logitransport.es",
            city="Zaragoza",
            sector=Sector.LOGISTICS,
            size=CompanySize.MEDIUM,
            employee_count=85,
            products_services=["transporte nacional", "almacenaje", "last mile"],
            technologies_used=["SAP", "Excel"],
            description="Empresa de logística y transporte de mercancías",
            pain_points=["digitalización", "tracking en tiempo real", "gestión de flotas"],
            status=LeadStatus.VALIDATED,
        ),
        Company(
            id="demo_006",
            name="HealthTech Soluciones",
            domain="healthtech.es",
            website="https://healthtech.es",
            email="info@healthtech.es",
            city="Bilbao",
            sector=Sector.HEALTH,
            size=CompanySize.SMALL,
            employee_count=30,
            products_services=["telemedicina", "gestión de citas", "historia clínica electrónica"],
            technologies_used=["React", "Node.js", "MongoDB"],
            description="Plataforma de telemedicina para clínicas privadas",
            pain_points=["cumplimiento RGPD", "integración con sistemas hospitalarios"],
            status=LeadStatus.VALIDATED,
        ),
    ]

    # ─── Iniciar orquestador con datos de ejemplo ────────────
    orch = Orchestrator()
    orch.companies = sample_companies

    print(f"📊 {len(sample_companies)} empresas de ejemplo cargadas\n")

    # ─── Fase 2: Clustering ──────────────────────────────────
    print("═" * 50)
    print("FASE 2: CLUSTERING")
    print("═" * 50)

    companies, profiles = await orch.run_phase_2(n_clusters=3)

    print(f"\n📋 Clusters generados:")
    for p in profiles:
        print(f"  Cluster {p.cluster_id}: {p.label}")
        print(f"    Empresas: {p.company_count} | Score medio: {p.avg_score}")
        print(f"    Tono recomendado: {p.recommended_tone.value}")
        print(f"    Pain points: {', '.join(p.key_pain_points[:3])}")
        print()

    # ─── Fase 3: Outreach (Dry Run) ─────────────────────────
    print("═" * 50)
    print("FASE 3: OUTREACH (DRY RUN)")
    print("═" * 50)

    drafts = await orch.run_phase_3(dry_run=True)

    print(f"\n✅ {len(drafts)} emails generados en modo preview")
    print("\nPara enviar emails reales:")
    print("  1. Configura SMTP en .env")
    print("  2. Ejecuta: python -m agents.orchestrator --live")


async def demo_full_pipeline():
    """
    Demo del pipeline completo con scraping real.
    Requiere API keys configuradas en .env.
    """
    orch = Orchestrator()

    metrics = await orch.run_full_pipeline(
        query="agencias de marketing digital Madrid",
        sources=["google_maps"],
        max_results=20,
        n_clusters=3,
        dry_run=True,
    )

    print(f"\n📊 Resultados del pipeline:")
    print(f"  Empresas scrapeadas: {metrics.total_scraped}")
    print(f"  Emails generados: {metrics.total_emails_sent}")


if __name__ == "__main__":
    asyncio.run(demo_with_sample_data())
