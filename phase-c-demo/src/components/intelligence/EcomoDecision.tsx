import Badge from "../shared/Badge";
import { decisionOptions, ecomoDecision } from "../../data/intelligenceDemoData";

export default function EcomoDecision() {
  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 10 }}>
        <h3 style={{ fontSize: 14 }}>Decisión ECOMO · Go / No-Go</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: precomputed_demo</div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: 14 }}>
        {decisionOptions.map((o) => (
          <div
            key={o.id}
            style={{
              padding: 12,
              border: o.selected ? "2px solid var(--color-blue)" : "1px solid var(--color-border)",
              background: o.selected ? "#EFF6FF" : "#fff",
              borderRadius: 6,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 18, fontWeight: 700, color: o.selected ? "var(--color-blue)" : "var(--color-muted)" }}>{o.id}</span>
              {o.selected && <Badge status="VALIDATED" small>SELECTED</Badge>}
            </div>
            <div style={{ fontWeight: 600, fontSize: 13, marginTop: 4 }}>{o.title}</div>
            <div style={{ fontSize: 12, color: "var(--color-muted)", marginTop: 4 }}>{o.description}</div>
          </div>
        ))}
      </div>

      <div style={{ padding: 10, background: "#FFFBEB", border: "1px solid #FDE68A", borderRadius: 6, fontSize: 12, marginBottom: 12 }}>
        ⚠ <strong>Limitación de datos:</strong> {ecomoDecision.limitation}
      </div>

      <div style={{ padding: 14, background: "var(--color-navy)", color: "#fff", borderRadius: 8 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <Badge status="WARNING">{ecomoDecision.outcome}</Badge>
          <div style={{ fontWeight: 700, fontSize: 14 }}>Output del agente</div>
        </div>
        <div style={{ marginTop: 8, fontSize: 13 }}>{ecomoDecision.reason}</div>
      </div>
    </div>
  );
}
