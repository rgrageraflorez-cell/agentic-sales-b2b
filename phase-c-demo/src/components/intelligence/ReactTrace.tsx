import { useState } from "react";
import type { ReactStep } from "../../types/intelligence";

interface Props { trace: ReactStep[]; }

const COLORS = {
  reason: "var(--color-blue)",
  act: "var(--color-cyan)",
  observe: "var(--color-green)",
  next: "var(--color-amber)",
};

export default function ReactTrace({ trace }: Props) {
  const [open, setOpen] = useState(true);
  return (
    <div className="card" style={{ padding: 0, marginBottom: 16, overflow: "hidden" }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: "100%",
          padding: 14,
          background: "#F8FAFC",
          border: 0,
          borderBottom: open ? "1px solid var(--color-border)" : 0,
          cursor: "pointer",
          textAlign: "left",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <div style={{ fontWeight: 600, fontSize: 14 }}>ReAct trace · razonamiento explícito</div>
          <div style={{ fontSize: 11, color: "var(--color-muted)" }}>
            {trace.length} pasos · cada uno con Reason / Act / Observe / Next decision
          </div>
        </div>
        <span style={{ fontSize: 14, color: "var(--color-muted)" }}>{open ? "▾" : "▸"}</span>
      </button>
      {open && (
        <div style={{ padding: 14 }}>
          {trace.map((s) => (
            <div key={s.step} style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: "var(--color-muted)", letterSpacing: 0.5, textTransform: "uppercase", marginBottom: 6 }}>
                Step {s.step}
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 10 }}>
                <Card title="Reason"        color={COLORS.reason}  text={s.reason} />
                <Card title="Act"           color={COLORS.act}     text={s.act} />
                <Card title="Observe"       color={COLORS.observe} text={s.observe} />
                <Card title="Next decision" color={COLORS.next}    text={s.nextDecision} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Card({ title, color, text }: { title: string; color: string; text: string }) {
  return (
    <div style={{ borderLeft: `3px solid ${color}`, padding: "8px 10px", background: "#fff", borderTop: "1px solid var(--color-border)", borderRight: "1px solid var(--color-border)", borderBottom: "1px solid var(--color-border)", borderRadius: 4 }}>
      <div style={{ fontSize: 10, fontWeight: 700, color, textTransform: "uppercase", letterSpacing: 0.4, marginBottom: 4 }}>{title}</div>
      <div style={{ fontSize: 12 }}>{text}</div>
    </div>
  );
}
