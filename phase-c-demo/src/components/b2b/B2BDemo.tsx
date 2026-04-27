import { useState } from "react";
import PipelineConsole from "./PipelineConsole";
import AgentFlow from "./AgentFlow";
import LearningPanel from "./LearningPanel";
import { LeadFunnelChart, SequencePerformanceChart, GeoChart, HumanizerScoreChart } from "./B2BCharts";
import { dryRunDefault } from "../../data/b2bDemoData";

const PHASES = [
  { name: "Collection",   note: "Scraping + enrichment + validación de email" },
  { name: "Intelligence", note: "Clustering + scoring + cluster profiles" },
  { name: "Outreach",     note: "Copywriter + Humanizer + Sender + Follow-up" },
  { name: "Learning",     note: "Wilson lower bounds + memoria persistente" },
];

export default function B2BDemo() {
  const [running, setRunning] = useState(false);
  const [currentPhase, setCurrentPhase] = useState(0);
  const [selectedPhase, setSelectedPhase] = useState(0);
  const [dryRun, setDryRun] = useState(dryRunDefault);

  const phaseToShow = running ? currentPhase : selectedPhase;

  return (
    <div>
      <PipelineConsole
        running={running}
        setRunning={setRunning}
        currentPhase={currentPhase}
        setCurrentPhase={setCurrentPhase}
      />

      <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: 16 }}>
        <div>
          <div style={{ fontSize: 11, color: "var(--color-muted)", textTransform: "uppercase", fontWeight: 700, letterSpacing: 0.4, marginBottom: 8 }}>Phase stepper</div>
          {PHASES.map((p, i) => {
            const active = i === phaseToShow;
            return (
              <button
                key={p.name}
                onClick={() => !running && setSelectedPhase(i)}
                disabled={running}
                style={{
                  width: "100%",
                  textAlign: "left",
                  padding: "12px 14px",
                  marginBottom: 6,
                  border: "1px solid var(--color-border)",
                  borderLeft: active ? "4px solid var(--color-blue)" : "4px solid var(--color-border)",
                  background: active ? "#EFF6FF" : "#fff",
                  borderRadius: 6,
                  cursor: running ? "not-allowed" : "pointer",
                  opacity: running && !active ? 0.6 : 1,
                }}
              >
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <span style={{ color: "var(--color-muted)", fontWeight: 700 }}>{i + 1}</span>
                  <span style={{ fontWeight: 600, fontSize: 13 }}>{p.name}</span>
                </div>
                <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 2 }}>{p.note}</div>
              </button>
            );
          })}
        </div>

        <div>
          <AgentFlow phase={phaseToShow} dryRun={dryRun} setDryRun={setDryRun} />
        </div>
      </div>

      <div style={{ marginTop: 16, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <LeadFunnelChart />
        <GeoChart />
      </div>
      <div style={{ marginTop: 12, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <SequencePerformanceChart />
        <HumanizerScoreChart />
      </div>

      <LearningPanel />
    </div>
  );
}
