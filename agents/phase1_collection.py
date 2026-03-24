"""
Fase 1: Agentes de recolección de datos.
- ScraperAgent: Busca empresas en múltiples fuentes
- EnricherAgent: Enriquece los datos con información adicional
- ValidatorAgent: Limpia, valida y deduplica
"""

from __future__ import annotations
import hashlib
import re
from datetime import datetime
from typing import Any

import httpx
from bs4 import BeautifulSoup

from agents.base import BaseAgent
from models import Company, CompanySize, ContactPerson, LeadStatus, Sector


# ─── Agente Scraper ──────────────────────────────────────────

class ScraperAgent(BaseAgent):
    """Busca empresas en múltiples fuentes de datos."""

    def __init__(self):
        super().__init__(
            name="Scraper",
            description="Recopila datos de empresas desde Google Maps, directorios y la web",
        )
        self.http = httpx.AsyncClient(timeout=30, follow_redirects=True)

    async def execute(
        self,
        query: str = "empresas tecnología Madrid",
        sources: list[str] | None = None,
        max_results: int = 100,
    ) -> list[Company]:
        """Ejecuta el scraping en las fuentes configuradas."""
        sources = sources or ["google_maps", "web_directories"]
        all_companies: list[Company] = []

        for source in sources:
            self.log_step(f"Scrapeando fuente: {source}", query)
            try:
                if source == "google_maps":
                    companies = await self._scrape_google_maps(query, max_results)
                elif source == "web_directories":
                    companies = await self._scrape_directories(query, max_results)
                elif source == "linkedin":
                    companies = await self._scrape_linkedin(query, max_results)
                else:
                    self.logger.warning(f"Fuente desconocida: {source}")
                    continue

                for c in companies:
                    c.source = source
                    c.scraped_at = datetime.now()
                    c.id = self._generate_id(c)
                all_companies.extend(companies)

            except Exception as e:
                self.logger.error(f"Error scrapeando {source}: {e}")

        self.log_step("Scraping completado", f"{len(all_companies)} empresas encontradas")
        return all_companies

    async def _scrape_google_maps(self, query: str, max_results: int) -> list[Company]:
        """
        Scraping via Google Maps / Places API.
        Requiere GOOGLE_MAPS_API_KEY en .env.
        Si no hay API key, usa scraping web como fallback.
        """
        import os
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")

        if api_key:
            return await self._google_places_api(query, max_results, api_key)

        # Fallback: generar estructura para búsqueda manual
        self.logger.info("Sin Google Maps API key — usando búsqueda web genérica")
        return await self._web_search_fallback(query, max_results)

    async def _google_places_api(self, query: str, max_results: int, api_key: str) -> list[Company]:
        """Usa Google Places API para buscar empresas."""
        companies = []
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {"query": query, "key": api_key, "language": "es"}

        resp = await self.http.get(url, params=params)
        data = resp.json()

        for result in data.get("results", [])[:max_results]:
            company = Company(
                name=result.get("name", ""),
                address=result.get("formatted_address", ""),
                google_rating=result.get("rating"),
                google_reviews=result.get("user_ratings_total"),
            )
            # Obtener detalles adicionales
            place_id = result.get("place_id")
            if place_id:
                detail = await self._get_place_details(place_id, api_key)
                company.phone = detail.get("phone", "")
                company.website = detail.get("website", "")
            companies.append(company)

        return companies

    async def _get_place_details(self, place_id: str, api_key: str) -> dict:
        """Obtiene detalles de un lugar de Google Places."""
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "key": api_key,
            "fields": "formatted_phone_number,website,url",
        }
        resp = await self.http.get(url, params=params)
        result = resp.json().get("result", {})
        return {
            "phone": result.get("formatted_phone_number", ""),
            "website": result.get("website", ""),
        }

    async def _web_search_fallback(self, query: str, max_results: int) -> list[Company]:
        """Fallback: scraping de directorios web públicos."""
        # Ejemplo con Páginas Amarillas o similar
        companies = []
        search_url = f"https://www.paginasamarillas.es/search/{query.replace(' ', '-')}"

        try:
            resp = await self.http.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, "html.parser")

            for listing in soup.select(".listado-item")[:max_results]:
                name_el = listing.select_one(".nombre-empresa")
                phone_el = listing.select_one(".telefono")
                addr_el = listing.select_one(".direccion")

                if name_el:
                    companies.append(Company(
                        name=name_el.get_text(strip=True),
                        phone=phone_el.get_text(strip=True) if phone_el else "",
                        address=addr_el.get_text(strip=True) if addr_el else "",
                    ))
        except Exception as e:
            self.logger.warning(f"Web search fallback falló: {e}")

        return companies

    async def _scrape_directories(self, query: str, max_results: int) -> list[Company]:
        """Scraping de directorios empresariales (e-informa, axesor, etc.)."""
        # Placeholder — cada directorio requiere su propia implementación
        self.logger.info("Directorio scraping: implementar según fuentes específicas")
        return []

    async def _scrape_linkedin(self, query: str, max_results: int) -> list[Company]:
        """Scraping de LinkedIn (requiere cookies o API)."""
        self.logger.info("LinkedIn scraping: requiere configuración de auth")
        return []

    def _generate_id(self, company: Company) -> str:
        """Genera un ID único para la empresa."""
        raw = f"{company.name}:{company.domain or company.website}:{company.city}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ─── Agente Enriquecedor ─────────────────────────────────────

class EnricherAgent(BaseAgent):
    """Enriquece los datos de empresas con información adicional."""

    def __init__(self):
        super().__init__(
            name="Enriquecedor",
            description="Enriquece datos: website, empleados, sector, contactos clave",
        )
        self.http = httpx.AsyncClient(timeout=20, follow_redirects=True)

    async def execute(self, companies: list[Company]) -> list[Company]:
        """Enriquece una lista de empresas."""
        enriched = []
        for i, company in enumerate(companies):
            self.log_step(f"Enriqueciendo {i+1}/{len(companies)}", company.name)
            try:
                company = await self._enrich_from_website(company)
                company = await self._classify_with_llm(company)
                company = await self._find_contacts(company)
                company.status = LeadStatus.ENRICHED
                company.last_updated = datetime.now()
            except Exception as e:
                self.logger.warning(f"Error enriqueciendo {company.name}: {e}")
            enriched.append(company)

        return enriched

    async def _enrich_from_website(self, company: Company) -> Company:
        """Extrae información del sitio web escaneando home + páginas de contacto."""
        if not company.website:
            return company

        from urllib.parse import urlparse, urljoin
        base_url = company.website
        company.domain = urlparse(base_url).netloc

        # Páginas a escanear en orden de prioridad
        pages_to_scan = [
            base_url,
            urljoin(base_url, "/contacto"),
            urljoin(base_url, "/contact"),
            urljoin(base_url, "/sobre-nosotros"),
            urljoin(base_url, "/quienes-somos"),
            urljoin(base_url, "/about"),
        ]

        found_emails: list[str] = []
        found_phones: list[str] = []
        description_set = False

        for url in pages_to_scan:
            try:
                resp = await self.http.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                    timeout=10,
                )
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")

                # Meta description solo en homepage
                if url == base_url and not description_set:
                    meta = soup.find("meta", attrs={"name": "description"})
                    if meta and meta.get("content"):
                        company.description = meta["content"][:500]
                        description_set = True

                # 1. Emails en atributos mailto: (más fiables)
                for a in soup.find_all("a", href=re.compile(r"^mailto:", re.I)):
                    email = a["href"].replace("mailto:", "").split("?")[0].strip().lower()
                    if email and "@" in email:
                        found_emails.append(email)

                # 2. Emails en el footer (zona de contacto habitual)
                footer = soup.find("footer")
                if footer:
                    footer_text = footer.get_text()
                    found_emails += re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", footer_text)

                # 3. Emails en todo el texto
                full_text = soup.get_text()
                found_emails += re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", full_text)

                # 4. Teléfonos
                found_phones += re.findall(
                    r"(?:\+34\s?)?(?:9\d{2}|6\d{2}|7\d{2})[\s.\-]?\d{3}[\s.\-]?\d{3}", full_text
                )

            except Exception:
                continue  # Silencioso — la página puede no existir

        # Filtrar y asignar mejor email
        if not company.email:
            skip = {"example", "test", "noreply", "no-reply", "donotreply",
                    "sentry", "png", "jpg", "gif", "webp", "woff", ".min"}
            for email in found_emails:
                email = email.lower().strip()
                if not any(s in email for s in skip) and len(email) < 80:
                    company.email = email
                    break

        # Asignar teléfono si no hay
        if not company.phone and found_phones:
            company.phone = found_phones[0]

        return company

    async def _classify_with_llm(self, company: Company) -> Company:
        """Usa LLM para clasificar sector, tamaño estimado, etc."""
        prompt = f"""Analiza esta empresa y devuelve un JSON con la clasificación:

Empresa: {company.name}
Web: {company.website}
Descripción: {company.description}
Dirección: {company.address}, {company.city}
Productos/servicios conocidos: {', '.join(company.products_services) if company.products_services else 'desconocidos'}

Devuelve SOLO un JSON con este formato exacto:
{{
    "sector": "tecnología|retail|salud|finanzas|manufactura|educación|hostelería|construcción|logística|otro",
    "estimated_employees": 25,
    "estimated_revenue": 500000,
    "products_services": ["servicio1", "servicio2"],
    "technologies": ["tech1", "tech2"],
    "pain_points": ["posible punto de dolor 1", "punto de dolor 2"],
    "description_enriched": "Descripción breve enriquecida de la empresa"
}}"""

        try:
            result = await self.llm_call(prompt, response_format="json", temperature=0.2)

            sector_map = {s.value: s for s in Sector}
            sector_str = result.get("sector", "otro")
            company.sector = sector_map.get(sector_str, Sector.OTHER)

            emp = result.get("estimated_employees", 0)
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

        except Exception as e:
            self.logger.warning(f"Error en clasificación LLM para {company.name}: {e}")

        return company

    async def _find_contacts(self, company: Company) -> Company:
        """Intenta encontrar contactos clave de la empresa."""
        if not company.domain:
            return company

        # Aquí se integrarían APIs como Apollo, Hunter.io, etc.
        # Placeholder: buscar en el sitio web
        prompt = f"""Basándote en esta empresa, sugiere los roles clave a contactar:
Empresa: {company.name}
Sector: {company.sector}
Tamaño: {company.size}
Nuestros servicios: {os.getenv('COMPANY_SERVICES', 'consultoría tecnológica')}

Devuelve SOLO un JSON con formato:
[
    {{"name": "", "role": "CEO/CTO/Director Comercial/etc", "email_pattern": "nombre@{company.domain}"}}
]"""
        try:
            import os
            result = await self.llm_call(prompt, response_format="json", temperature=0.2)
            for contact_data in result:
                company.contacts.append(ContactPerson(
                    role=contact_data.get("role", ""),
                    email=contact_data.get("email_pattern", ""),
                ))
        except Exception:
            pass

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

        # Paso 1: Limpieza de datos
        companies = [self._clean_company(c) for c in companies]

        # Paso 2: Deduplicación
        companies = self._deduplicate(companies)

        # Paso 3: Validación de campos críticos
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
        """Limpia los datos de una empresa."""
        c.name = c.name.strip().title() if c.name else ""
        c.email = c.email.strip().lower() if c.email else ""
        c.phone = re.sub(r"[^\d+]", "", c.phone) if c.phone else ""
        c.website = c.website.strip().rstrip("/") if c.website else ""

        if c.website and not c.website.startswith("http"):
            c.website = f"https://{c.website}"

        return c

    def _deduplicate(self, companies: list[Company]) -> list[Company]:
        """Elimina duplicados basándose en nombre normalizado + dominio."""
        seen: dict[str, Company] = {}
        for c in companies:
            key = self._dedup_key(c)
            if key not in seen:
                seen[key] = c
            else:
                # Merge: quedarse con el que tenga más datos
                existing = seen[key]
                seen[key] = self._merge(existing, c)
        return list(seen.values())

    def _dedup_key(self, c: Company) -> str:
        """Genera una clave de deduplicación."""
        name = re.sub(r"[^a-z0-9]", "", c.name.lower())
        domain = c.domain or ""
        return f"{name}:{domain}"

    def _merge(self, a: Company, b: Company) -> Company:
        """Fusiona dos registros de la misma empresa."""
        for field in a.model_fields:
            val_a = getattr(a, field)
            val_b = getattr(b, field)
            if not val_a and val_b:
                setattr(a, field, val_b)
        return a

    def _is_valid(self, c: Company) -> bool:
        """Verifica si la empresa tiene datos mínimos para continuar."""
        has_name = bool(c.name and len(c.name) > 2)
        has_contact = bool(c.email or c.phone or c.website)
        return has_name and has_contact
