"""
PainPointDetectorAgent — Detecta señales REALES de necesidad escaneando web, noticias y ofertas de empleo.
"""

from __future__ import annotations
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from agents.base import BaseAgent
from models import Company


# ─── Definiciones de señales ────────────────────────────────

SIGNAL_DEFINITIONS = {
    "crecimiento_reciente": {
        "weight": 9,
        "keywords": [
            "apertura", "inauguración", "inauguramos", "expansión", "crecimiento",
            "récord de ventas", "nueva tienda", "nuevo local", "ampliación",
        ],
    },
    "expansion_geografica": {
        "weight": 8,
        "keywords": [
            "nueva sede", "presencia en", "mercado internacional", "nueva delegación",
            "abrimos en", "expansión a", "nueva oficina",
        ],
    },
    "ecommerce_activo": {
        "weight": 8,
        "keywords": [
            "tienda online", "añadir al carrito", "checkout", "shopify",
            "woocommerce", "prestashop", "comprar online", "envío gratis",
        ],
    },
    "multicategoria": {
        "weight": 7,
        "keywords": [
            "catálogo amplio", "marcas", "colecciones", "líneas de negocio",
            "categorías", "gama de productos", "portfolio",
        ],
    },
    "estacionalidad_visible": {
        "weight": 7,
        "keywords": [
            "temporada", "black friday", "rebajas", "campaña navidad",
            "campaña de verano", "ofertas de temporada", "vuelta al cole",
        ],
    },
    "contratacion_data": {
        "weight": 10,
        "keywords": [
            "data analyst", "business intelligence", "power bi", "tableau",
            "analista de datos", "data scientist", "big data", "bi developer",
        ],
    },
    "transformacion_digital": {
        "weight": 6,
        "keywords": [
            "digitalización", "innovación tecnológica", "industria 4.0",
            "transformación digital", "automatización", "smart factory",
        ],
    },
    "red_comercial": {
        "weight": 8,
        "keywords": [
            "delegados", "distribuidores", "franquicias", "puntos de venta",
            "red comercial", "agentes comerciales", "representantes",
        ],
    },
    "campañas_activas": {
        "weight": 6,
        "keywords": [
            "lanzamiento", "promoción", "nuevo producto", "nueva colección",
            "campaña", "descuento especial",
        ],
    },
    "multicanal": {
        "weight": 7,
        "keywords": [
            "amazon", "marketplace", "omnicanal", "mayorista",
            "minorista", "canal online", "canal físico", "b2b y b2c",
        ],
    },
}


class PainPointDetectorAgent(BaseAgent):
    """Detecta señales reales de necesidad escaneando web, noticias y empleo."""

    def __init__(self):
        super().__init__(
            name="Detector de Pain Points",
            description="Escanea web, noticias y empleo para detectar señales reales de necesidad",
        )
        self.http = httpx.AsyncClient(timeout=20, follow_redirects=True)

    async def execute(self, companies: list[Company]) -> list[Company]:
        """Detecta pain points reales para cada empresa."""
        self.log_step("Detectando pain points", f"{len(companies)} empresas")

        for i, company in enumerate(companies):
            self.log_step(f"Escaneando {i+1}/{len(companies)}", company.name)
            try:
                signals = await self._detect_signals(company)
                company._signals_data = signals

                # Sintetizar con LLM
                if signals.get("signals_found"):
                    synthesis = await self._synthesize_pain_points(company, signals)
                    company.pain_points = synthesis.get("pain_points", company.pain_points)
                    signals["arigra_angle"] = synthesis.get("arigra_angle", "")
                    signals["opening_hook"] = synthesis.get("opening_hook", "")
                    signals["signal_score"] = synthesis.get("signal_score", 0)

                    # Boost al lead_score basado en señales
                    boost = min(25, signals["signal_score"] * 0.25)
                    company.lead_score = min(100, company.lead_score + boost)

            except Exception as e:
                self.logger.warning(f"Error detectando señales para {company.name}: {e}")
                company._signals_data = {}

        self.log_step("Detección completada")
        return companies

    async def _detect_signals(self, company: Company) -> dict:
        """Detecta señales de las 3 fuentes."""
        signals: dict[str, Any] = {"signals_found": [], "total_weight": 0}

        # Fuente 1: Web de la empresa
        web_signals = await self._scan_website(company)
        signals["web_signals"] = web_signals

        # Fuente 2: Noticias
        news_signals = await self._scan_news(company)
        signals["news_signals"] = news_signals

        # Fuente 3: Ofertas de empleo
        job_signals = await self._scan_job_postings(company)
        signals["job_signals"] = job_signals

        # Consolidar
        all_found = web_signals + news_signals + job_signals
        signals["signals_found"] = all_found
        signals["total_weight"] = sum(s.get("weight", 0) for s in all_found)

        return signals

    async def _scan_website(self, company: Company) -> list[dict]:
        """Escanea la web de la empresa buscando señales."""
        if not company.website:
            return []

        signals_found = []
        pages_to_check = ["", "/about", "/productos", "/blog", "/servicios", "/nosotros"]

        for page in pages_to_check:
            url = company.website.rstrip("/") + page
            try:
                resp = await self.http.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code != 200:
                    continue
                text = resp.text.lower()

                for signal_type, definition in SIGNAL_DEFINITIONS.items():
                    for keyword in definition["keywords"]:
                        if keyword.lower() in text:
                            # Extraer contexto (80 chars antes y después)
                            idx = text.find(keyword.lower())
                            start = max(0, idx - 80)
                            end = min(len(text), idx + len(keyword) + 80)
                            context = text[start:end].strip()
                            context = re.sub(r"<[^>]+>", "", context)  # Limpiar HTML

                            signals_found.append({
                                "type": signal_type,
                                "keyword": keyword,
                                "source": "website",
                                "page": page or "/",
                                "context": context[:200],
                                "weight": definition["weight"],
                            })
                            break  # Una señal por tipo por página

            except Exception:
                continue

        return signals_found

    async def _scan_news(self, company: Company) -> list[dict]:
        """Busca noticias recientes sobre la empresa."""
        signals_found = []
        search_query = f"{company.name} {company.city or ''}".strip()

        try:
            url = f"https://news.google.com/search?q={search_query}&hl=es&gl=ES"
            resp = await self.http.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            headlines = [a.get_text(strip=True) for a in soup.select("article a")][:10]

            for headline in headlines:
                headline_lower = headline.lower()
                for signal_type, definition in SIGNAL_DEFINITIONS.items():
                    for keyword in definition["keywords"]:
                        if keyword.lower() in headline_lower:
                            signals_found.append({
                                "type": signal_type,
                                "keyword": keyword,
                                "source": "news",
                                "context": headline[:200],
                                "weight": definition["weight"],
                            })
                            break

        except Exception:
            pass

        return signals_found

    async def _scan_job_postings(self, company: Company) -> list[dict]:
        """Busca si la empresa está contratando perfiles de datos."""
        signals_found = []
        search_query = f"{company.name} empleo data analyst business intelligence"

        try:
            url = f"https://www.google.com/search?q={search_query}"
            resp = await self.http.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                return []

            text = resp.text.lower()
            data_keywords = [
                "data analyst", "business intelligence", "analista de datos",
                "data scientist", "power bi", "tableau", "big data",
            ]
            for kw in data_keywords:
                if kw in text:
                    signals_found.append({
                        "type": "contratacion_data",
                        "keyword": kw,
                        "source": "job_postings",
                        "context": f"{company.name} está buscando perfiles de {kw}",
                        "weight": 10,
                    })
                    break

        except Exception:
            pass

        return signals_found

    async def _synthesize_pain_points(self, company: Company, signals: dict) -> dict:
        """Usa LLM para sintetizar las señales en pain points accionables."""
        signals_summary = []
        for s in signals.get("signals_found", []):
            signals_summary.append(
                f"- [{s['type']}] (fuente: {s['source']}, peso: {s['weight']}): {s['context']}"
            )

        prompt = f"""Analiza las señales detectadas para esta empresa y genera pain points concretos.

EMPRESA: {company.name}
SECTOR: {company.sector.value if company.sector else 'desconocido'}
TAMAÑO: {company.size.value if company.size else 'desconocido'} ({company.employee_count or '?'} empleados)
PRODUCTOS: {', '.join(company.products_services[:5]) if company.products_services else 'desconocidos'}

SEÑALES DETECTADAS:
{chr(10).join(signals_summary)}

SERVICIOS DE ARIGRA DISPONIBLES:
- Previsión de ventas (series temporales, modelos predictivos)
- Dashboard ejecutivo (visualización de KPIs de negocio)
- Análisis por producto (rendimiento, ciclo de vida, portfolio)
- Análisis geográfico (ventas por zona, delegación, territorio)
- Segmentación de clientes (clusters, valor de cliente, retención)
- Oportunidades comerciales (cross-sell, up-sell, nuevos mercados)
- Análisis de campañas (ROI, atribución, estacionalidad)

Devuelve SOLO JSON:
{{
    "pain_points": ["2-4 problemas CONCRETOS conectados con las señales detectadas"],
    "arigra_angle": "El servicio de ARIGRA que mejor encaja y por qué",
    "opening_hook": "Una frase de apertura personalizada para el email que demuestre que hemos investigado",
    "signal_score": 75
}}

El signal_score va de 0 a 100 según lo prometedor que sea el lead basándose en las señales."""

        try:
            result = await self.llm_call(prompt, response_format="json", temperature=0.3)
            return result
        except Exception as e:
            self.logger.warning(f"Error sintetizando pain points para {company.name}: {e}")
            return {"pain_points": company.pain_points, "signal_score": 0}
