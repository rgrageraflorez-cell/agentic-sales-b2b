"""Modelos de datos para el sistema de captación de clientes."""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, PrivateAttr


# ─── Enums ────────────────────────────────────────────────────

class CompanySize(str, Enum):
    MICRO = "micro"          # 1-9 empleados
    SMALL = "pequeña"        # 10-49
    MEDIUM = "mediana"       # 50-249
    LARGE = "grande"         # 250+

class Sector(str, Enum):
    TECH = "tecnología"
    RETAIL = "retail"
    HEALTH = "salud"
    FINANCE = "finanzas"
    MANUFACTURING = "manufactura"
    EDUCATION = "educación"
    HOSPITALITY = "hostelería"
    CONSTRUCTION = "construcción"
    LOGISTICS = "logística"
    OTHER = "otro"

class LeadStatus(str, Enum):
    RAW = "raw"                    # Recién scrapeado
    ENRICHED = "enriched"          # Datos enriquecidos
    VALIDATED = "validated"        # Validado y limpio
    CLUSTERED = "clustered"        # Asignado a cluster
    SCORED = "scored"              # Con puntuación
    EMAIL_DRAFTED = "email_drafted"
    EMAIL_SENT = "email_sent"
    EMAIL_OPENED = "email_opened"
    REPLIED = "replied"
    CONVERTED = "converted"
    REJECTED = "rejected"

class EmailTone(str, Enum):
    FORMAL = "formal"
    FRIENDLY = "cercano"
    DIRECT = "directo"
    CONSULTATIVE = "consultivo"


# ─── Core Models ──────────────────────────────────────────────

class ContactPerson(BaseModel):
    name: str = ""
    role: str = ""
    email: str = ""
    linkedin_url: str = ""
    phone: str = ""


class Company(BaseModel):
    """Modelo principal de empresa/lead."""
    id: Optional[str] = None
    name: str
    domain: str = ""
    website: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    city: str = ""
    province: str = ""
    country: str = "España"
    
    # Clasificación
    sector: Optional[Sector] = None
    cnae_code: str = ""
    size: Optional[CompanySize] = None
    employee_count: Optional[int] = None
    revenue_estimate: Optional[float] = None
    year_founded: Optional[int] = None
    
    # Productos y servicios
    products_services: list[str] = Field(default_factory=list)
    technologies_used: list[str] = Field(default_factory=list)
    description: str = ""
    
    # Contactos
    contacts: list[ContactPerson] = Field(default_factory=list)
    
    # Scoring y clustering
    cluster_id: Optional[int] = None
    cluster_label: str = ""
    lead_score: float = 0.0
    pain_points: list[str] = Field(default_factory=list)
    
    # Estado
    status: LeadStatus = LeadStatus.RAW
    source: str = ""
    scraped_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    
    # Social
    linkedin_url: str = ""
    google_rating: Optional[float] = None
    google_reviews: Optional[int] = None

    # Atributos dinámicos v2 (añadidos por agentes nuevos)
    _signals_data: dict = PrivateAttr(default_factory=dict)
    _diagnostic: dict = PrivateAttr(default_factory=dict)
    _role_strategy: dict = PrivateAttr(default_factory=dict)


class ClusterProfile(BaseModel):
    """Perfil de un cluster de empresas."""
    cluster_id: int
    label: str
    description: str
    
    # Características del cluster
    avg_size: CompanySize = CompanySize.SMALL
    primary_sector: Sector = Sector.OTHER
    avg_score: float = 0.0
    company_count: int = 0
    
    # Estrategia de email
    recommended_tone: EmailTone = EmailTone.FRIENDLY
    key_pain_points: list[str] = Field(default_factory=list)
    value_propositions: list[str] = Field(default_factory=list)
    subject_line_templates: list[str] = Field(default_factory=list)


class EmailDraft(BaseModel):
    """Email generado para una empresa."""
    company_id: str
    company_name: str
    recipient_email: str
    recipient_name: str = ""
    
    subject: str
    body_html: str
    body_text: str
    
    cluster_id: int
    tone: EmailTone
    personalization_notes: str = ""
    
    # Estado
    sent: bool = False
    sent_at: Optional[datetime] = None
    opened: bool = False
    replied: bool = False
    
    # Follow-up
    follow_up_count: int = 0
    next_follow_up: Optional[datetime] = None


class PipelineMetrics(BaseModel):
    """Métricas del pipeline completo."""
    total_scraped: int = 0
    total_enriched: int = 0
    total_validated: int = 0
    total_clustered: int = 0
    total_emails_sent: int = 0
    total_opened: int = 0
    total_replied: int = 0
    total_converted: int = 0
    
    clusters: list[ClusterProfile] = Field(default_factory=list)
    
    @property
    def open_rate(self) -> float:
        if self.total_emails_sent == 0:
            return 0.0
        return self.total_opened / self.total_emails_sent
    
    @property
    def reply_rate(self) -> float:
        if self.total_emails_sent == 0:
            return 0.0
        return self.total_replied / self.total_emails_sent
    
    @property
    def conversion_rate(self) -> float:
        if self.total_emails_sent == 0:
            return 0.0
        return self.total_converted / self.total_emails_sent
