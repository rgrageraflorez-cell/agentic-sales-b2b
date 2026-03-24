"""
Fase 2: Agentes de clustering inteligente.
- ClassifierAgent: Clasifica empresas por múltiples dimensiones
- ScorerAgent: Asigna puntuación de prioridad a cada lead
- SegmenterAgent: Agrupa empresas en clusters accionables
"""

from __future__ import annotations
import json
from typing import Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder

from agents.base import BaseAgent
from models import (
    ClusterProfile, Company, CompanySize, EmailTone,
    LeadStatus, Sector,
)


# ─── Agente Clasificador ─────────────────────────────────────

class ClassifierAgent(BaseAgent):
    """Clasifica empresas en múltiples dimensiones usando LLM + reglas."""

    def __init__(self):
        super().__init__(
            name="Clasificador",
            description="Clasifica empresas por tamaño, sector, madurez digital, etc.",
        )

    async def execute(self, companies: list[Company]) -> list[Company]:
        """Clasifica todas las empresas."""
        self.log_step("Clasificando empresas", f"{len(companies)} empresas")

        for company in companies:
            # Clasificación basada en reglas
            company = self._rule_based_classification(company)

            # Enriquecimiento con LLM para casos ambiguos
            if not company.sector or company.sector == Sector.OTHER:
                company = await self._llm_classification(company)

        self.log_step("Clasificación completada")
        return companies

    def _rule_based_classification(self, c: Company) -> Company:
        """Clasificación basada en reglas heurísticas."""
        # Tamaño por empleados si lo tenemos
        if c.employee_count:
            if c.employee_count < 10:
                c.size = CompanySize.MICRO
            elif c.employee_count < 50:
                c.size = CompanySize.SMALL
            elif c.employee_count < 250:
                c.size = CompanySize.MEDIUM
            else:
                c.size = CompanySize.LARGE

        # Sector por keywords en descripción/productos
        text = f"{c.description} {' '.join(c.products_services)}".lower()
        sector_keywords = {
            Sector.TECH: ["software", "app", "digital", "saas", "cloud", "ia", "datos", "web"],
            Sector.RETAIL: ["tienda", "comercio", "venta", "ecommerce", "retail"],
            Sector.HEALTH: ["salud", "clínica", "médico", "farmacia", "hospital"],
            Sector.FINANCE: ["banco", "seguros", "inversión", "fintech", "contabilidad"],
            Sector.MANUFACTURING: ["fábrica", "producción", "industrial", "manufactura"],
            Sector.EDUCATION: ["formación", "academia", "colegio", "universidad", "educación"],
            Sector.HOSPITALITY: ["hotel", "restaurante", "turismo", "hostelería"],
            Sector.CONSTRUCTION: ["construcción", "obra", "inmobiliaria", "arquitectura"],
            Sector.LOGISTICS: ["transporte", "logística", "envío", "almacén"],
        }
        for sector, keywords in sector_keywords.items():
            if any(kw in text for kw in keywords):
                c.sector = sector
                break

        return c

    async def _llm_classification(self, company: Company) -> Company:
        """Usa LLM para clasificar empresas que las reglas no resolvieron."""
        prompt = f"""Clasifica esta empresa. Responde SOLO con JSON:

Empresa: {company.name}
Descripción: {company.description}
Productos: {', '.join(company.products_services)}
Web: {company.website}

JSON:
{{
    "sector": "tecnología|retail|salud|finanzas|manufactura|educación|hostelería|construcción|logística|otro",
    "confidence": 0.85
}}"""
        try:
            result = await self.llm_call(prompt, response_format="json", temperature=0.1)
            sector_map = {s.value: s for s in Sector}
            company.sector = sector_map.get(result["sector"], Sector.OTHER)
        except Exception as e:
            self.logger.debug(f"LLM classification falló para {company.name}: {e}")
        return company


# ─── Agente Scorer ────────────────────────────────────────────

class ScorerAgent(BaseAgent):
    """Asigna puntuación de prioridad (lead scoring) a cada empresa."""

    def __init__(self, weights: dict[str, float] | None = None):
        super().__init__(
            name="Scorer",
            description="Puntuación de leads basada en fit, intención y accesibilidad",
        )
        # Pesos configurables para el scoring
        self.weights = weights or {
            "has_email": 25,
            "has_website": 15,
            "has_phone": 10,
            "has_contact_person": 20,
            "right_size": 15,         # Tamaño ideal para nuestros servicios
            "good_sector": 15,        # Sector alineado
            "good_rating": 10,        # Rating en Google
            "has_pain_points": 15,    # Puntos de dolor identificados
            "has_technologies": 10,   # Stack tecnológico visible
        }

    async def execute(
        self,
        companies: list[Company],
        ideal_sizes: list[CompanySize] | None = None,
        ideal_sectors: list[Sector] | None = None,
    ) -> list[Company]:
        """Puntúa y ordena todas las empresas."""
        ideal_sizes = ideal_sizes or [CompanySize.SMALL, CompanySize.MEDIUM]
        ideal_sectors = ideal_sectors or [Sector.TECH, Sector.RETAIL, Sector.FINANCE]

        self.log_step("Scoring de leads", f"{len(companies)} empresas")

        for company in companies:
            score = 0.0

            # Accesibilidad (datos de contacto)
            if company.email:
                score += self.weights["has_email"]
            if company.website:
                score += self.weights["has_website"]
            if company.phone:
                score += self.weights["has_phone"]
            if company.contacts:
                score += self.weights["has_contact_person"]

            # Fit (tamaño y sector ideal)
            if company.size in ideal_sizes:
                score += self.weights["right_size"]
            if company.sector in ideal_sectors:
                score += self.weights["good_sector"]

            # Señales de calidad
            if company.google_rating and company.google_rating >= 4.0:
                score += self.weights["good_rating"]
            if company.pain_points:
                score += self.weights["has_pain_points"]
            if company.technologies_used:
                score += self.weights["has_technologies"]

            # Normalizar a 0-100
            max_possible = sum(self.weights.values())
            company.lead_score = round((score / max_possible) * 100, 1)
            company.status = LeadStatus.SCORED

        # Ordenar por score descendente
        companies.sort(key=lambda c: c.lead_score, reverse=True)

        self.log_step("Scoring completado", f"Top score: {companies[0].lead_score if companies else 0}")
        return companies


# ─── Agente Segmentador ──────────────────────────────────────

class SegmenterAgent(BaseAgent):
    """Agrupa empresas en clusters accionables para personalizar outreach."""

    def __init__(self, n_clusters: int = 5):
        super().__init__(
            name="Segmentador",
            description="Agrupación en clusters para personalización de emails",
        )
        self.n_clusters = n_clusters

    async def execute(self, companies: list[Company]) -> tuple[list[Company], list[ClusterProfile]]:
        """Segmenta empresas en clusters."""
        self.log_step("Segmentando empresas", f"{len(companies)} empresas → {self.n_clusters} clusters")

        if len(companies) == 0:
            self.log_step("Segmentación omitida", "No hay empresas para segmentar")
            return companies, []

        if len(companies) < self.n_clusters:
            self.n_clusters = max(1, len(companies) // 2) if len(companies) > 1 else 1

        # Paso 1: Vectorizar empresas
        features, feature_names = self._vectorize(companies)

        # Paso 2: KMeans clustering
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features_scaled)

        # Paso 3: Asignar clusters
        for company, label in zip(companies, labels):
            company.cluster_id = int(label)
            company.status = LeadStatus.CLUSTERED

        # Paso 4: Generar perfiles de cluster
        profiles = await self._generate_cluster_profiles(companies)

        # Asignar label del cluster a cada empresa
        profile_map = {p.cluster_id: p for p in profiles}
        for company in companies:
            if company.cluster_id in profile_map:
                company.cluster_label = profile_map[company.cluster_id].label

        self.log_step("Segmentación completada", f"{len(profiles)} clusters creados")
        return companies, profiles

    def _vectorize(self, companies: list[Company]) -> tuple[np.ndarray, list[str]]:
        """Convierte empresas en vectores numéricos para clustering."""
        size_encoder = LabelEncoder()
        sector_encoder = LabelEncoder()

        sizes = [c.size.value if c.size else "unknown" for c in companies]
        sectors = [c.sector.value if c.sector else "unknown" for c in companies]

        size_encoded = size_encoder.fit_transform(sizes)
        sector_encoded = sector_encoder.fit_transform(sectors)

        features = []
        for i, c in enumerate(companies):
            vec = [
                size_encoded[i],
                sector_encoded[i],
                c.employee_count or 0,
                c.revenue_estimate or 0,
                c.lead_score,
                c.google_rating or 0,
                len(c.products_services),
                len(c.technologies_used),
                len(c.pain_points),
                1 if c.email else 0,
                1 if c.website else 0,
            ]
            features.append(vec)

        feature_names = [
            "size", "sector", "employees", "revenue", "score",
            "rating", "n_products", "n_technologies", "n_pain_points",
            "has_email", "has_website",
        ]
        return np.array(features, dtype=float), feature_names

    async def _generate_cluster_profiles(self, companies: list[Company]) -> list[ClusterProfile]:
        """Genera perfiles descriptivos para cada cluster usando LLM."""
        clusters: dict[int, list[Company]] = {}
        for c in companies:
            clusters.setdefault(c.cluster_id, []).append(c)

        profiles = []
        for cluster_id, members in clusters.items():
            # Resumen estadístico del cluster
            sizes = [m.size.value for m in members if m.size]
            sectors = [m.sector.value for m in members if m.sector]
            avg_score = np.mean([m.lead_score for m in members])
            all_pains = []
            for m in members:
                all_pains.extend(m.pain_points)

            sample_names = [m.name for m in members[:5]]

            prompt = f"""Analiza este cluster de empresas y genera un perfil. Responde SOLO con JSON:

Empresas de ejemplo: {', '.join(sample_names)}
Tamaños predominantes: {', '.join(set(sizes))}
Sectores predominantes: {', '.join(set(sectors))}
Score medio: {avg_score:.1f}
Pain points encontrados: {', '.join(set(all_pains[:10]))}
Número de empresas: {len(members)}

JSON:
{{
    "label": "Etiqueta corta del cluster (ej: 'Pymes tech en crecimiento')",
    "description": "Descripción del perfil del cluster en 2 frases",
    "recommended_tone": "formal|cercano|directo|consultivo",
    "key_pain_points": ["pain1", "pain2", "pain3"],
    "value_propositions": ["propuesta1", "propuesta2"],
    "subject_line_templates": ["Asunto email 1", "Asunto email 2"]
}}"""

            try:
                result = await self.llm_call(prompt, response_format="json", temperature=0.4)

                tone_map = {t.value: t for t in EmailTone}
                most_common_size = max(set(sizes), key=sizes.count) if sizes else "pequeña"
                most_common_sector = max(set(sectors), key=sectors.count) if sectors else "otro"

                profile = ClusterProfile(
                    cluster_id=cluster_id,
                    label=result.get("label", f"Cluster {cluster_id}"),
                    description=result.get("description", ""),
                    avg_size=CompanySize(most_common_size) if most_common_size in [s.value for s in CompanySize] else CompanySize.SMALL,
                    primary_sector=Sector(most_common_sector) if most_common_sector in [s.value for s in Sector] else Sector.OTHER,
                    avg_score=round(avg_score, 1),
                    company_count=len(members),
                    recommended_tone=tone_map.get(result.get("recommended_tone", "cercano"), EmailTone.FRIENDLY),
                    key_pain_points=result.get("key_pain_points", []),
                    value_propositions=result.get("value_propositions", []),
                    subject_line_templates=result.get("subject_line_templates", []),
                )
                profiles.append(profile)

            except Exception as e:
                self.logger.error(f"Error generando perfil cluster {cluster_id}: {e}")
                profiles.append(ClusterProfile(
                    cluster_id=cluster_id,
                    label=f"Cluster {cluster_id}",
                    description="Perfil no generado",
                    company_count=len(members),
                ))

        return profiles
