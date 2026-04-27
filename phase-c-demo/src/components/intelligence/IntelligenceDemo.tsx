import { useState } from "react";
import {
  reportData,
  anomalies,
  reactTrace,
  osintSources,
  amcAnalysis,
  scenarios,
  confidenceIndex,
  lowConfidenceIndex,
  claims,
  strategyPlan,
} from "../../data/intelligenceDemoData";
import Badge from "../shared/Badge";
import ConfidenceMeter from "../shared/ConfidenceMeter";
import MetricCard from "../shared/MetricCard";
import AgentNode from "../shared/AgentNode";
import ReactTrace from "./ReactTrace";
import EvidenceTable from "./EvidenceTable";
import AMCTable from "./AMCTable";
import ScenarioMatrix from "./ScenarioMatrix";
import EcomoDecision from "./EcomoDecision";
import ConfidencePanel from "./ConfidencePanel";
import SilenceProtocol from "./SilenceProtocol";
import ClaimVerifier from "./ClaimVerifier";
import HumanReviewPanel from "./HumanReviewPanel";
import KpiTrend from "./charts/KpiTrend";
import FunnelChart from "./charts/FunnelChart";
import TrafficMix from "./charts/TrafficMix";
import AmcRadarChart from "./charts/AmcRadarChart";
import OsintGraph from "./charts/OsintGraph";
import AnomalyTimeline from "./charts/AnomalyTimeline";
import ContentBrief from "./cognitive/ContentBrief";

export default function IntelligenceDemo() {
  const [silence, setSilence] = useState(false);
  const ci = silence ? lowConfidenceIndex : confidenceIndex;

  return (
    <div>
      {/* Strategic question banner */}
      <div
        style={{
          background: "#FEF3C7",
          border: "1px solid #FDE68A",
          padding: 14,
          borderRadius: 8,
          marginBottom: 12,
        }}
      >
        <div style={{ fontSize: 11, fontWeight: 700, color: "var(--color-amber)", textTransform: "uppercase", letterSpacing: 0.5 }}>Strategic Question</div>
        <div style={{ fontSize: 14, fontWeight: 600, marginTop: 4 }}>
          ¿Debe Club Foto Nauta aumentar la inversión publicitaria tras el informe de febrero 2026?
        </div>
      </div>

      {/* Sticky confidence bar */}
      <div
        style={{
          position: "sticky",
          top: 56,
          zIndex: 5,
          background: "#fff",
          border: "1px solid var(--color-border)",
          borderRadius: 8,
          padding: 12,
          marginBottom: 12,
          display: "flex",
          alignItems: "center",
          gap: 14,
          boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
        }}
      >
        <ConfidenceMeter score={ci.finalIndex * 100} label="Confidence index" mode={ci.mode} />
        <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, fontWeight: 500, marginLeft: "auto", whiteSpace: "nowrap" }}>
          <input type="checkbox" checked={silence} onChange={(e) => setSilence(e.target.checked)} />
          Simulate insufficient evidence
        </label>
      </div>

      {silence ? (
        <SilenceProtocol onResume={() => setSilence(false)} />
      ) : (
        <>
          {/* Report KPIs */}
          <Section title={`Reporte mensual recibido · ${reportData.client} · ${reportData.period}`} dataSource={reportData.dataSource}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 10 }}>
              {reportData.kpis.map((k) => (
                <MetricCard
                  key={k.metric}
                  label={k.metric}
                  value={k.value}
                  delta={k.delta}
                  direction={k.direction}
                  notes={k.notes}
                />
              ))}
            </div>
          </Section>

          <Section title="Tendencia 12 meses + mix de tráfico" dataSource="provided_report" raw>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <KpiTrend />
              <TrafficMix />
            </div>
          </Section>

          <Section title="Funnel de checkout + detección de anomalías" dataSource="provided_report" raw>
            <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 12 }}>
              <FunnelChart />
              <AnomalyTimeline />
            </div>
          </Section>

          {/* Anomalies */}
          <Section title="Anomalías detectadas (PreDiagnosticAgent)" dataSource="precomputed_demo">
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 10 }}>
              {anomalies.map((a) => {
                const sev = a.severity === "high" ? "BLOCKED" : a.severity === "medium" ? "WARNING" : "VALIDATED";
                return (
                  <div key={a.id} className="card" style={{ padding: 12, borderLeft: `4px solid ${a.severity === "high" ? "var(--color-red)" : a.severity === "medium" ? "var(--color-amber)" : "var(--color-green)"}` }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                      <div style={{ fontWeight: 600, fontSize: 13 }}>{a.metric}</div>
                      <Badge status={sev} small />
                    </div>
                    <div style={{ fontSize: 12, color: "var(--color-muted)", marginTop: 2 }}>{a.value}</div>
                    <div style={{ marginTop: 8, fontSize: 11, fontWeight: 700, color: "var(--color-muted)", letterSpacing: 0.4, textTransform: "uppercase" }}>
                      {a.interpretationStatus.replace(/_/g, " ")}
                    </div>
                    <div style={{ fontSize: 12, marginTop: 4 }}>{a.nextAction}</div>
                  </div>
                );
              })}
            </div>
          </Section>

          {/* Agent flow */}
          <Section title="Flujo de agentes (CI)" dataSource="precomputed_demo">
            <AgentNode
              name="OSINTCollector"
              status="VALIDATED"
              input="Reporte Nauta + sector fotografía"
              output="7 fuentes recolectadas, 5 validadas"
              tool="web scraping + APIs sociales"
              confidence={0.78}
              dataSource="REAL"
            />
            <AgentNode gate name="GATE · Triangulación" gateNote="Solo se aceptan claims con ≥2 fuentes independientes. 1 fuente bloqueada (Foro NáuticaPro)." />
            <div style={{ height: 8 }} />
            <AgentNode
              name="Analyst"
              status="VALIDATED"
              input="KPIs + OSINT validado"
              output="Hipótesis: fricción checkout móvil"
              tool="ReAct loop (3 pasos)"
              confidence={0.72}
              dataSource="PRECOMPUTED"
            />
            <AgentNode gate name="GATE · ClaimVerifier" gateNote="Bloquea afirmaciones causales sin replicación: 2 claims BLOCKED, 3 APPROVED." />
            <div style={{ height: 8 }} />
            <AgentNode
              name="StrategyPlanner"
              status="WARNING"
              input="Hipótesis validada parcialmente"
              output="Decisión: CONDITIONAL NO-GO (auditar funnel primero)"
              tool="ECOMO framework"
              confidence={0.68}
              dataSource="PRECOMPUTED"
            />
            <AgentNode gate name="GATE · Confianza ≥ 0.50" gateNote="Confidence index = 0.68 (LIMITED). Pasa el umbral pero exige revisión humana." />
            <div style={{ height: 8 }} />
            <AgentNode
              name="HumanReviewer"
              status="WARNING"
              input="Output del StrategyPlanner"
              output="Pendiente de aprobación (panel inferior)"
              tool="UI panel + audit log"
              dataSource="PRECOMPUTED"
            />
          </Section>

          <Section title="Razonamiento ReAct" dataSource="precomputed_demo" raw>
            <ReactTrace trace={reactTrace} />
          </Section>

          <Section title="Evidencia OSINT · grafo de triangulación + tabla" dataSource="mixed" raw>
            <OsintGraph />
            <div style={{ height: 12 }} />
            <EvidenceTable sources={osintSources} />
          </Section>

          <Section title="Análisis competitivo (AMC) + radar" dataSource="precomputed_demo" raw>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <AMCTable entries={amcAnalysis} />
              <AmcRadarChart />
            </div>
          </Section>

          <Section title="Escenarios + decisión ECOMO" dataSource="precomputed_demo" raw>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <ScenarioMatrix scenarios={scenarios} />
              <EcomoDecision />
            </div>
          </Section>

          <Section title="Índice de confianza" dataSource="precomputed_demo" raw>
            <ConfidencePanel ci={ci} />
          </Section>

          <Section title="Output cognitivo · brief de contenido para Club Foto Nauta" dataSource="precomputed_demo" raw>
            <ContentBrief />
          </Section>

          <Section title="Claim verifier" dataSource="precomputed_demo" raw>
            <ClaimVerifier claims={claims} />
          </Section>

          <Section title="Plan de acción" dataSource={strategyPlan.dataSource}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
              {(["immediate", "shortTerm", "structural"] as const).map((k) => (
                <div key={k} className="card" style={{ padding: 12 }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: "var(--color-muted)", textTransform: "uppercase", letterSpacing: 0.4, marginBottom: 8 }}>
                    {k === "immediate" ? "Inmediato" : k === "shortTerm" ? "Corto plazo" : "Estructural"}
                  </div>
                  {strategyPlan[k].map((a, i) => (
                    <div key={i} style={{ borderTop: i === 0 ? 0 : "1px solid var(--color-border)", padding: "8px 0" }}>
                      <div style={{ fontSize: 12, fontWeight: 500 }}>{a.text}</div>
                      <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 4 }}>
                        owner: {a.owner} · KPI: {a.kpi} · {a.horizon}
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </Section>

          <Section title="Revisión humana final" dataSource="precomputed_demo" raw>
            <HumanReviewPanel />
          </Section>
        </>
      )}
    </div>
  );
}

function Section({ title, dataSource, children, raw }: { title: string; dataSource: string; children: React.ReactNode; raw?: boolean }) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <h2 style={{ fontSize: 14 }}>{title}</h2>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: {dataSource}</div>
      </div>
      {raw ? children : <div>{children}</div>}
    </div>
  );
}
