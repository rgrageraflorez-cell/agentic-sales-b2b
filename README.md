# Sistema Agéntico de Captación de Clientes B2B

Sistema multi-agente para automatizar la prospección comercial: recopilación de datos de empresas, clustering inteligente y envío de emails personalizados.

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                ORQUESTADOR CENTRAL                  │
├──────────┬──────────────┬──────────────────────────┤
│  FASE 1  │    FASE 2    │         FASE 3           │
│ Scraping │  Clustering  │   Outreach Email          │
│          │              │                           │
│ Scraper  │ Clasificador │ Copywriter                │
│ Enricher │ Scorer       │ Sender                    │
│ Validator│ Segmentador  │ Follow-up                 │
└──────────┴──────────────┴──────────────────────────┘
```

## Instalación

```bash
pip install -r requirements.txt
cp .env.example .env  # Configurar API keys
python -m agents.orchestrator --run
```

## Configuración (.env)

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...            # Alternativa
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu@email.com
SMTP_PASSWORD=app-password
COMPANY_NAME=Tu Empresa
COMPANY_SERVICES=descripción de servicios
```

## Uso

```python
from agents.orchestrator import Orchestrator

orch = Orchestrator()

# Paso 1: Recopilar empresas
orch.run_phase_1(
    sources=["google_maps", "linkedin", "directorios"],
    query="empresas tecnología Madrid",
    max_results=200
)

# Paso 2: Clusterizar
orch.run_phase_2()

# Paso 3: Enviar emails
orch.run_phase_3(dry_run=True)  # Preview primero
orch.run_phase_3(dry_run=False) # Enviar
```
