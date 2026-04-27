import Badge from "../shared/Badge";
import type { AMCEntry, AMCDimension } from "../../types/intelligence";

interface Props { entries: AMCEntry[]; }

function Row({ label, dim }: { label: string; dim: AMCDimension }) {
  return (
    <div style={{ borderTop: "1px solid var(--color-border)", padding: "8px 0" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: "var(--color-muted)", letterSpacing: 0.4, textTransform: "uppercase", minWidth: 90 }}>{label}</span>
        <Badge status={dim.level} small />
      </div>
      <div style={{ fontSize: 12, color: "var(--color-text)" }}>{dim.justification}</div>
    </div>
  );
}

export default function AMCTable({ entries }: Props) {
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 10 }}>
        <h3 style={{ fontSize: 14 }}>AMC · Awareness / Motivation / Capability</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: precomputed_demo</div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 12 }}>
        {entries.map((e) => (
          <div key={e.competitor} className="card" style={{ padding: 14 }}>
            <div style={{ fontWeight: 700, fontSize: 13 }}>{e.competitor}</div>
            <div style={{ fontSize: 11, color: "var(--color-muted)", marginBottom: 4 }}>{e.type}</div>
            <Row label="Awareness"  dim={e.awareness} />
            <Row label="Motivation" dim={e.motivation} />
            <Row label="Capability" dim={e.capability} />
            <div style={{ marginTop: 10, paddingTop: 10, borderTop: "2px solid var(--color-text)", fontSize: 12 }}>
              <div><strong>Probabilidad de respuesta:</strong> {e.responseProbability}</div>
              <div style={{ color: "var(--color-muted)", marginTop: 2 }}><strong>Timeline:</strong> {e.timeline}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
