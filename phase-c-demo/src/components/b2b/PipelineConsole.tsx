import { useEffect, useRef, useState } from "react";
import Badge from "../shared/Badge";
import { agentLogs } from "../../data/agentLogs";
import { finalSummary } from "../../data/b2bDemoData";

interface Props {
  running: boolean;
  setRunning: (r: boolean) => void;
  currentPhase: number;
  setCurrentPhase: (p: number) => void;
}

const PHASES = ["Collection", "Intelligence", "Outreach", "Learning"];

export default function PipelineConsole({ running, setRunning, currentPhase, setCurrentPhase }: Props) {
  const [logs, setLogs] = useState<typeof agentLogs>([]);
  const [done, setDone] = useState(false);
  const consoleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!running) return;
    setLogs([]);
    setDone(false);
    setCurrentPhase(0);

    let i = 0;
    const tick = () => {
      if (i >= agentLogs.length) {
        setRunning(false);
        setDone(true);
        return;
      }
      const next = agentLogs[i];
      setLogs((prev) => [...prev, next]);
      setCurrentPhase(next.phase - 1);
      i++;
      setTimeout(tick, 300);
    };
    const start = setTimeout(tick, 250);
    return () => clearTimeout(start);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running]);

  useEffect(() => {
    if (consoleRef.current) consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
  }, [logs]);

  return (
    <div className="card" style={{ padding: 16, marginBottom: 16 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: 14 }}>Pipeline Console</div>
          <div style={{ fontSize: 11, color: "var(--color-muted)" }}>
            source: precomputed_demo · trazas tomadas de la salida real del orquestador ARIGRA
          </div>
        </div>
        <button
          onClick={() => setRunning(true)}
          disabled={running}
          style={{
            background: running ? "#94a3b8" : "var(--color-blue)",
            color: "#fff",
            border: 0,
            padding: "8px 16px",
            borderRadius: 6,
            fontWeight: 600,
            fontSize: 13,
            cursor: running ? "default" : "pointer",
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          {running && <span className="spinner" style={{ borderTopColor: "#fff" }} />}
          {running ? "Running..." : done ? "Re-run Daily Pipeline" : "Run Daily Pipeline"}
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 6, marginBottom: 12 }}>
        {PHASES.map((p, i) => {
          const active = running && currentPhase === i;
          const passed = (running || done) && i < currentPhase + (done ? 1 : 0);
          const completed = done || passed;
          return (
            <div
              key={p}
              style={{
                padding: "8px 10px",
                borderRadius: 6,
                border: "1px solid var(--color-border)",
                background: active ? "#DBEAFE" : completed ? "#DCFCE7" : "#F8FAFC",
                fontSize: 12,
                fontWeight: 600,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ color: "var(--color-muted)" }}>{i + 1}.</span> {p}
                {active && <span className="spinner" style={{ marginLeft: "auto" }} />}
                {completed && !active && <span style={{ marginLeft: "auto", color: "var(--color-green)" }}>✓</span>}
              </div>
            </div>
          );
        })}
      </div>

      <div
        ref={consoleRef}
        className="mono"
        style={{
          background: "#0B1F3A",
          color: "#E2E8F0",
          padding: 12,
          borderRadius: 6,
          height: 240,
          overflowY: "auto",
        }}
      >
        {logs.length === 0 && (
          <div style={{ color: "#64748B" }}>$ waiting for orchestrator.run()…</div>
        )}
        {logs.map((l, i) => (
          <div key={i} className="fade-in" style={{ marginBottom: 3 }}>
            <span style={{ color: "#64748B" }}>[{l.ts}]</span>{" "}
            <span style={{ color: "#20C7D9" }}>{l.agent}</span>:{" "}
            <span>{l.action}</span>{" "}
            <span style={{ color: "#94a3b8" }}>— {l.result}</span>
            {l.confidence !== undefined && (
              <span style={{ color: "#F59E0B" }}> [conf {(l.confidence * 100).toFixed(0)}%]</span>
            )}
          </div>
        ))}
        {done && (
          <div style={{ marginTop: 8, paddingTop: 8, borderTop: "1px dashed #334155", color: "#16A34A" }}>
            ✓ Pipeline complete · {finalSummary.emails_sent_dry_run} emails (dry_run) ·{" "}
            {finalSummary.clusters_active} clusters · {finalSummary.unclassifiable} unclassifiable ·{" "}
            {finalSummary.learning_records_updated} learning records updated
          </div>
        )}
      </div>

      {done && (
        <div style={{ marginTop: 10, display: "flex", gap: 8, alignItems: "center" }}>
          <Badge status="VALIDATED">Run finished</Badge>
          <span style={{ fontSize: 11, color: "var(--color-muted)" }}>
            source: precomputed_demo · ningún email real fue enviado
          </span>
        </div>
      )}
    </div>
  );
}
