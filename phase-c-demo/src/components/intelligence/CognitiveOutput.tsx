import Badge from "../shared/Badge";
import { cognitiveOutput } from "../../data/intelligenceDemoData";

export default function CognitiveOutput() {
  const c = cognitiveOutput;
  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 10 }}>
        <h3 style={{ fontSize: 14 }}>Output cognitivo · interpretación humanizada</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: precomputed_demo</div>
      </div>
      <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
        <Badge status={c.status} />
        <Badge status={c.confidence === "FULL" ? "FULL" : c.confidence === "LIMITADA" ? "LIMITADA" : "INSUFICIENTE"} />
      </div>
      <div
        style={{
          borderLeft: "4px solid var(--color-blue)",
          padding: "12px 14px",
          background: "#F8FAFC",
          borderRadius: 6,
          fontSize: 13,
          lineHeight: 1.6,
        }}
      >
        {c.summary}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 12 }}>
        <div style={{ padding: 12, background: "#F0FDF4", border: "1px solid #BBF7D0", borderRadius: 6 }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: "var(--color-green)", textTransform: "uppercase", letterSpacing: 0.4 }}>Key finding</div>
          <div style={{ fontSize: 13, marginTop: 4 }}>{c.keyFinding}</div>
        </div>
        <div style={{ padding: 12, background: "#FFFBEB", border: "1px solid #FDE68A", borderRadius: 6 }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: "var(--color-amber)", textTransform: "uppercase", letterSpacing: 0.4 }}>Main uncertainty</div>
          <div style={{ fontSize: 13, marginTop: 4 }}>{c.mainUncertainty}</div>
        </div>
      </div>
    </div>
  );
}
