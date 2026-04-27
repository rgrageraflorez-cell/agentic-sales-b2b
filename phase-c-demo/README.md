# ARIGRA · Phase C Demo

Demo visual del trabajo de la **Fase C** del proyecto ARIGRA. Muestra dos sistemas
agénticos:

1. **B2B Lead Generation Agent** — el pipeline real ya operativo en `agents/`.
2. **Competitive Intelligence Agent** — prototipo aplicado al cliente real
   *Club Foto Nauta* (febrero 2026).

> Este proyecto vive en `phase-c-demo/` y **no toca nada** del código Python
> de ARIGRA. Es 100% frontend.

---

## 1 · Qué es esta demo

Una SPA (Vite + React + TypeScript + TailwindCSS por CDN) que ilustra cómo
ARIGRA opera como **sistema agéntico**: agentes especializados, decisiones
condicionales, gates de validación, ReAct, índice de confianza con protocolo
de silencio, claim verifier y revisión humana al final.

Toda dato visible lleva su **etiqueta de origen** (`real_pipeline_output`,
`provided_report`, `precomputed_demo`, `simulated_realistic`,
`real_scraping`, `provided_data`).

## 2 · Cómo correrla en local

```bash
cd phase-c-demo
npm install
npm run dev          # http://localhost:5173
```

Build y preview de producción:

```bash
npm run build        # tsc + vite build → dist/
npm run preview      # sirve dist/ en http://localhost:4173
```

## 3 · Cómo desplegarla en GitHub Pages

Opción A — **GitHub Actions** (incluido en `.github/workflows/deploy.yml`):

1. Subir el repo a GitHub.
2. En Settings → Pages → Source: *GitHub Actions*.
3. Cualquier push a `main` que toque `phase-c-demo/**` despliega automáticamente.

Opción B — **manual** (rama `gh-pages`):

```bash
cd phase-c-demo
npm run deploy       # build + gh-pages -d dist
```

> En `vite.config.ts` el `base` es `"./"` para que funcione bajo cualquier
> sub-ruta. El routing usa `HashRouter`, así que las URLs son
> `https://…/#/b2b`, `https://…/#/intelligence`, etc.

## 4 · Qué es real vs precomputado

| Dato                                          | Origen                       | Etiqueta UI            |
| --------------------------------------------- | ---------------------------- | ---------------------- |
| Conteos de Phase 1 (25 / 22 / 17 / 5 / 3)     | Salida real `phase1_companies.json` (extrapolado) | `real_pipeline_output` |
| Sample de empresas (Fotografiarte, Raúl Ortega…) | `phase1_companies.json` real | `real_pipeline_output` |
| Perfiles de cluster 0 / 2 / 4 / -1            | `phase2_profiles.json` real  | `real_pipeline_output` |
| Email "Before / After" humanizer              | `phase3_drafts.json` real + reescritura humanizer | `real_pipeline_output` |
| KPIs por campaña + Wilson lower bounds        | Simulado realista (3 campañas) | `simulated_realistic` |
| Logs del orquestador                          | Reconstrucción a partir de `agents/orchestrator.py` | `precomputed_demo` |
| KPIs Club Foto Nauta febrero 2026             | Mock realista (informe simulado) | `provided_report` |
| Reseñas Google / Trustpilot / prensa local    | Pre-recolectado (no llamada en vivo) | `real_scraping` / `precomputed_demo` |
| AMC, escenarios, claims, plan de acción       | Construido para la demo      | `precomputed_demo` |

**Nada se envía a APIs externas desde el frontend.** No hay claves, no hay
llamadas a Resend/IMAP/scraping. El toggle `dry_run` en la fase Outreach
es ilustrativo.

## 5 · Cómo conecta con el sistema B2B existente

El backend Python (en la carpeta padre) ejecuta:

```
ScraperAgent → EnrichmentAgent → ValidatorAgent → PreDiagnosticAgent
            → ClassifierAgent → ScorerAgent → SegmenterAgent
            → PainPointAgent → RolePersonalizer → CopywriterAgent
            → HumanizerAgent → SenderAgent → FollowUpAgent
            → GmailWatcher / IMAPListener → LearningEngine
```

La demo lee la **estructura** de esa cadena (no llama a los procesos), y
muestra:

- conteos por fase tomados de los JSON en `data/`,
- perfiles de `phase2_profiles.json`,
- un email real de `phase3_drafts.json` reescrito por el humanizer,
- las trazas del orquestador como log streamado.

Para conectar la demo con un backend en vivo se reservaría una variable
`VITE_BACKEND_URL` en `.env`. **No está activada**: si se quisiera, las
funciones que producen datos vivirían detrás de `fetch(import.meta.env.VITE_BACKEND_URL + …)`
y devolverían el mismo `dataSource: "real_pipeline_output"` que las mocks.

## 6 · TN10–TN12 · checklist de capacidades

| Capacidad                              | TN   | Dónde se demuestra |
| -------------------------------------- | ---- | ------------------ |
| Razonamiento explícito (ReAct)         | TN10 | Intelligence · `ReactTrace` |
| Memoria persistente entre runs         | TN10 | B2B · `LearningPanel` (Wilson) |
| Pipeline multi-agente con gates        | TN10 | Intelligence · `AgentNode` + Gate cards |
| Verificación de claims                 | TN11 | Intelligence · `ClaimVerifier` |
| Triangulación OSINT (≥2 fuentes)       | TN11 | Intelligence · `EvidenceTable` |
| Análisis competitivo AMC               | TN11 | Intelligence · `AMCTable` |
| Protocolo de silencio                  | TN12 | Intelligence · checkbox sticky → `SilenceProtocol` |
| Índice de confianza ponderado          | TN12 | Intelligence · `ConfidencePanel` (sticky bar) |
| Revisión humana obligatoria            | TN12 | Intelligence · `HumanReviewPanel` |
| Decisión ECOMO Go / No-Go              | TN12 | Intelligence · `EcomoDecision` |

## 7 · Limitaciones conocidas

- Los KPIs de Club Foto Nauta son **simulados** (informe mensual mock). Si
  pasáis el informe real, sustituidlo en `src/data/intelligenceDemoData.ts`
  (constante `reportData`).
- El `dry_run` toggle es decorativo: no hay sender real conectado.
- La salida del LearningEngine (Wilson lower bounds) se muestra precomputada
  para 3 campañas de ejemplo — el cálculo real está en `agents/learning_engine.py`.
- El proyecto usa **TailwindCSS por CDN** para evitar la complejidad de
  configurar PostCSS; la mayor parte del estilado es CSS inline + variables
  CSS para mantener la coherencia visual.

## 8 · Demo script de 5 minutos

| Tiempo | Pestaña | Acción y guion |
| ------ | ------- | -------------- |
| 0:00 | Home | "Dos sistemas agénticos. El de la izquierda ya está en producción; el de la derecha es el prototipo de Inteligencia Competitiva." |
| 0:30 | /b2b | Click **Run Daily Pipeline**. "Mientras corre, fíjense en los gates: el Validator descarta 3, el Humanizer reescribe 17 emails." |
| 1:30 | /b2b · Phase 3 | Mostrar diff Before/After. "El humanizer es lo que diferencia un email IA de uno humano: quitar adverbios, formales, triadas." |
| 2:15 | /b2b · Learning | Señalar Wilson LB en los insights. "No usamos el porcentaje observado; usamos la cota inferior del intervalo de confianza para evitar conclusiones por azar." |
| 3:00 | /intelligence | Leer la pregunta estratégica + KPIs Nauta. "Las ventas caen 20% pero el ticket medio sube. ¿Subimos publicidad?" |
| 3:30 | ReactTrace | "El agente piensa en voz alta. Tres pasos. La conclusión es: NO subir, antes auditar el funnel." |
| 4:00 | EvidenceTable + ClaimVerifier | "2 reseñas no bastan para afirmar causa. El claim verifier lo bloquea explícitamente." |
| 4:30 | Sticky checkbox | Marcar **Simulate insufficient evidence**. "Si la confianza cae bajo 0.50, el agente entra en protocolo de silencio y se rehúsa a opinar." Desmarcar. |
| 4:50 | HumanReviewPanel | "Y nada sale al cliente sin firma analista. Approve / Edit / More evidence / Reject." |

---

**Autor:** Rodrigo Gragera Flórez · Co-fundador ARIGRA
**Versión:** 0.1 (Phase C visual demo)
