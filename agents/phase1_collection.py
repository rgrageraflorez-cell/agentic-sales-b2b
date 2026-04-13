"""
Fase 1: Agentes de recolección de datos (versión agéntica).
- ScraperAgent: Busca empresas autónomamente en internet (DuckDuckGo)
- EnricherAgent: Visita webs y extrae datos con LLM
- ValidatorAgent: Limpia, valida y deduplica
"""

from __future__ import annotations
import hashlib
import os
import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse, urljoin

import httpx
from bs4 import BeautifulSoup

from agents.base import BaseAgent
from models import Company, CompanySize, ContactPerson, LeadStatus, Sector


# ─── Agente Scraper (Agéntico) ──────────────────────────────────

class ScraperAgent(BaseAgent):
    """Busca empresas autónomamente en internet usando DuckDuckGo."""

    def __init__(self):
        super().__init__(
            name="Scraper",
            description="Busca empresas en internet de forma autónoma (DuckDuckGo + LLM)",
        )
        self.http = httpx.AsyncClient(timeout=30, follow_redirects=True)

    # Dominios que nunca son empresas reales
    BLOCKED_DOMAINS = {
        "wikipedia.org", "gov.br", "gov.es", "gob.es", "boe.es",
        "facebook.com", "twitter.com", "instagram.com", "linkedin.com",
        "youtube.com", "tiktok.com", "reddit.com", "amazon.com",
        "google.com", "bing.com", "yahoo.com",
        "elpais.com", "elmundo.es", "abc.es", "lavanguardia.com",
        "tripadvisor.com", "yelp.com",
    }

    async def execute(
        self,
        query: str = "empresas tecnología Madrid",
        sources: list[str] | None = None,
        max_results: int = 30,
    ) -> list[Company]:
        """Busca empresas en internet usando DuckDuckGo."""
        self.log_step("Buscando empresas en internet", query)

        # Paso 1: Buscar con múltiples queries para más cobertura
        all_results = []
        queries = self._build_search_queries(query)
        for q in queries:
            results = self._search_web(q, max_results)
            all_results.extend(results)

        # Deduplicar por URL
        seen_urls = set()
        raw_results = []
        for r in all_results:
            url = r.get("href", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                raw_results.append(r)

        self.log_step("Resultados de búsqueda", f"{len(raw_results)} URLs encontradas")

        # Paso 2: Filtrar dominios bloqueados y convertir en empresas
        companies = []
        for result in raw_results:
            url = result.get("href", "")
            domain = urlparse(url).netloc if url else ""

            # Filtrar dominios bloqueados
            if any(blocked in domain for blocked in self.BLOCKED_DOMAINS):
                continue

            company = Company(
                name=result.get("title", "").strip(),
                website=url,
                description=result.get("body", "")[:500],
                domain=domain,
            )
            if company.name and len(company.name) > 2:
                company.id = self._generate_id(company)
                company.source = "duckduckgo"
                company.scraped_at = datetime.now()
                companies.append(company)

        # Paso 3: Filtrar con LLM — quedarnos solo con empresas reales del sector buscado
        if companies:
            companies = await self._filter_real_companies(companies, query)

        self.log_step("Scraping completado", f"{len(companies)} empresas encontradas")
        return companies[:max_results]

    def _build_search_queries(self, base_query: str) -> list[str]:
        """Genera variaciones de búsqueda para encontrar más empresas."""
        queries = [base_query]
        # Añadir variaciones si la query no es muy larga
        if len(base_query.split()) <= 6:
            queries.append(f"{base_query} contacto email")
            queries.append(f"{base_query} directorio empresas")
        return queries

    def _search_web(self, query: str, max_results: int) -> list[dict]:
        """Busca en DuckDuckGo y devuelve resultados."""
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results * 2, region="es-es"))
                return results
        except ImportError:
            # Fallback al paquete antiguo
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=max_results * 2, region="es-es"))
                    return results
            except Exception as e:
                self.logger.error(f"Error en búsqueda DuckDuckGo: {e}")
                return []
        except Exception as e:
            self.logger.error(f"Error en búsqueda DuckDuckGo: {e}")
            return []

    async def _filter_real_companies(self, companies: list[Company], query: str) -> list[Company]:
        """Usa LLM para filtrar: quedarnos solo con empresas reales del sector."""
        names_list = "\n".join([
            f"{i+1}. {c.name} | {c.website} | {c.description[:100]}"
            for i, c in enumerate(companies[:40])
        ])

        prompt = f"""Analiza esta lista de resultados de búsqueda para la query "{query}".
Identifica cuáles son empresas REALES y privadas (NO páginas de gobierno, artículos de prensa,
blogs, directorios genéricos, Wikipedia, o páginas informativas).

Solo incluye empresas que:
- Tienen un sitio web corporativo propio
- Operan como negocio real (venden productos o servicios)
- Son relevantes para la búsqueda

Resultados:
{names_list}

Devuelve SOLO un JSON con los NÚMEROS de los resultados que son empresas reales:
{{"indices": [1, 3, 5]}}"""

        try:
            result = await self.llm_call(prompt, response_format="json", temperature=0.1)
            valid_indices = set(result.get("indices", []))
            if valid_indices:
                return [c for i, c in enumerate(companies[:40]) if (i + 1) in valid_indices]
        except Exception as e:
            self.logger.warning(f"Error filtrando empresas con LLM: {e}")

        return companies

    def _generate_id(self, company: Company) -> str:
        """Genera un ID único para la empresa."""
        raw = f"{company.name}:{company.domain or company.website}:{company.city}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ─── Agente Enriquecedor (Agéntico) ─────────────────────────────

class EnricherAgent(BaseAgent):
    """Visita las webs de las empresas y extrae datos con LLM."""

    def __init__(self):
        super().__init__(
            name="Enriquecedor",
            description="Visita webs corporativas y extrae datos con LLM",
        )
        self.http = httpx.AsyncClient(
            timeout=15,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )

    async def execute(self, companies: list[Company]) -> list[Company]:
        """Enriquece cada empresa visitando su web y extrayendo datos."""
        enriched = []
        for i, company in enumerate(companies):
            self.log_step(f"Enriqueciendo {i+1}/{len(companies)}", company.name)
            try:
                # Paso 1: Visitar web y extraer texto + emails + teléfonos
                company = await self._scan_website(company)

                # Paso 2: LLM analiza todo el contexto y clasifica
                company = await self._classify_with_llm(company)

                company.status = LeadStatus.ENRICHED
                company.last_updated = datetime.now()
            except Exception as e:
                self.logger.warning(f"Error enriqueciendo {company.name}: {e}")
            enriched.append(company)

        return enriched

    async def _scan_website(self, company: Company) -> Company:
        """Visita la web de la empresa y extrae emails, teléfonos, descripción."""
        if not company.website:
            return company

        base_url = company.website.rstrip("/")
        company.domain = urlparse(base_url).netloc

        # Páginas a escanear en orden de prioridad
        pages_to_scan = [
            base_url,
            urljoin(base_url + "/", "contacto"),
            urljoin(base_url + "/", "contact"),
            urljoin(base_url + "/", "contactanos"),
            urljoin(base_url + "/", "sobre-nosotros"),
            urljoin(base_url + "/", "quienes-somos"),
            urljoin(base_url + "/", "about"),
            urljoin(base_url + "/", "about-us"),
        ]

        found_emails: list[str] = []
        found_phones: list[str] = []
        all_text = ""

        for url in pages_to_scan:
            try:
                resp = await self.http.get(url, timeout=10)
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")

                # Meta description solo de la home
                if url == base_url and not company.description:
                    meta = soup.find("meta", attrs={"name": "description"})
                    if meta and meta.get("content"):
                        company.description = meta["content"][:500]

                # Emails en mailto: (más fiables)
                for a in soup.find_all("a", href=re.compile(r"^mailto:", re.I)):
                    email = a["href"].replace("mailto:", "").split("?")[0].strip().lower()
                    if email and "@" in email:
                        found_emails.append(email)

                # Emails en footer
                footer = soup.find("footer")
                if footer:
                    found_emails += re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", footer.get_text())

                # Emails en todo el texto
                page_text = soup.get_text(separator=" ", strip=True)
                found_emails += re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", page_text)

                # Teléfonos (España)
                found_phones += re.findall(
                    r"(?:\+34\s?)?(?:9\d{2}|6\d{2}|7\d{2})[\s.\-]?\d{3}[\s.\-]?\d{3}", page_text
                )

                # Acumular texto para que el LLM lo analice
                all_text += f"\n--- {url} ---\n{page_text[:2000]}"

            except Exception:
                continue

        # Filtrar y asignar email
        if not company.email:
            skip = {"example", "test", "noreply", "no-reply", "donotreply",
                    "sentry", "png", "jpg", "gif", "webp", "woff", ".min", ".css", ".js"}
            for email in found_emails:
                email = email.lower().strip()
                if not any(s in email for s in skip) and len(email) < 80 and "." in email.split("@")[-1]:
                    company.email = email
                    break

        # Asignar teléfono
        if not company.phone and found_phones:
            company.phone = found_phones[0]

        # Guardar texto para el LLM
        company._web_text = all_text[:4000]

        return company

    async def _classify_with_llm(self, company: Company) -> Company:
        """LLM analiza el texto de la web y extrae datos estructurados."""
        web_text = getattr(company, "_web_text", "")
        if not web_text and not company.description:
            return company

        prompt = f"""Analiza esta empresa basándote en el texto de su web y devuelve un JSON.

Empresa: {company.name}
Web: {company.website}
Email encontrado: {company.email or 'no encontrado'}
Teléfono encontrado: {company.phone or 'no encontrado'}
Descripción actual: {company.description or 'ninguna'}

Texto extraído de su web:
{web_text[:3000]}

Devuelve SOLO un JSON con este formato exacto:
{{
    "sector": "tecnología|retail|salud|finanzas|manufactura|educación|hostelería|construcción|logística|otro",
    "estimated_employees": 25,
    "estimated_revenue": 500000,
    "products_services": ["servicio1", "servicio2"],
    "technologies": ["tech1", "tech2"],
    "pain_points": ["punto de dolor 1", "punto de dolor 2"],
    "description_enriched": "Descripción breve y concisa de la empresa",
    "email_from_web": "email@empresa.com o null si no encontrado",
    "city": "ciudad donde opera"
}}"""

        try:
            result = await self.llm_call(prompt, response_format="json", temperature=0.2)

            sector_map = {s.value: s for s in Sector}
            company.sector = sector_map.get(result.get("sector", "otro"), Sector.OTHER)

            emp = result.get("estimated_employees") or 0
            if emp < 10:
                company.size = CompanySize.MICRO
            elif emp < 50:
                company.size = CompanySize.SMALL
            elif emp < 250:
                company.size = CompanySize.MEDIUM
            else:
                company.size = CompanySize.LARGE
            company.employee_count = emp

            company.revenue_estimate = result.get("estimated_revenue")
            company.products_services = result.get("products_services", [])
            company.technologies_used = result.get("technologies", [])
            company.pain_points = result.get("pain_points", [])

            if result.get("description_enriched"):
                company.description = result["description_enriched"]

            if result.get("city"):
                company.city = result["city"]

            # Si el LLM encontró un email que no teníamos
            llm_email = result.get("email_from_web")
            if llm_email and llm_email != "null" and not company.email:
                company.email = llm_email

        except Exception as e:
            self.logger.warning(f"Error en clasificación LLM para {company.name}: {e}")

        # Limpiar atributo temporal
        if hasattr(company, "_web_text"):
            del company._web_text

        return company


# ─── Agente Validador ─────────────────────────────────────────

class ValidatorAgent(BaseAgent):
    """Limpia, valida y deduplica los datos de empresas."""

    def __init__(self):
        super().__init__(
            name="Validador",
            description="Limpieza de datos, validación de emails, deduplicación",
        )

    async def execute(self, companies: list[Company]) -> list[Company]:
        """Valida y limpia la lista de empresas."""
        self.log_step("Iniciando validación", f"{len(companies)} empresas")

        companies = [self._clean_company(c) for c in companies]
        companies = self._deduplicate(companies)

        valid = []
        for c in companies:
            if self._is_valid(c):
                c.status = LeadStatus.VALIDATED
                valid.append(c)
            else:
                self.logger.debug(f"Empresa descartada: {c.name} (datos insuficientes)")

        self.log_step("Validación completada", f"{len(valid)} empresas válidas de {len(companies)}")
        return valid

    def _clean_company(self, c: Company) -> Company:
        c.name = c.name.strip().title() if c.name else ""
        c.email = c.email.strip().lower() if c.email else ""
        c.phone = re.sub(r"[^\d+]", "", c.phone) if c.phone else ""
        c.website = c.website.strip().rstrip("/") if c.website else ""
        if c.website and not c.website.startswith("http"):
            c.website = f"https://{c.website}"
        return c

    def _deduplicate(self, companies: list[Company]) -> list[Company]:
        seen: dict[str, Company] = {}
        for c in companies:
            key = self._dedup_key(c)
            if key not in seen:
                seen[key] = c
            else:
                seen[key] = self._merge(seen[key], c)
        return list(seen.values())

    def _dedup_key(self, c: Company) -> str:
        name = re.sub(r"[^a-z0-9]", "", c.name.lower())
        domain = c.domain or ""
        return f"{name}:{domain}"

    def _merge(self, a: Company, b: Company) -> Company:
        for field in a.model_fields:
            val_a = getattr(a, field)
            val_b = getattr(b, field)
            if not val_a and val_b:
                setattr(a, field, val_b)
        return a

    def _is_valid(self, c: Company) -> bool:
        has_name = bool(c.name and len(c.name) > 2)
        has_contact = bool(c.email or c.phone or c.website)
        return has_name and has_contact
