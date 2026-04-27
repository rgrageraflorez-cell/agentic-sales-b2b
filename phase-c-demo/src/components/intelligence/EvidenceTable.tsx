import Badge from "../shared/Badge";
import type { OsintSource } from "../../types/intelligence";

interface Props { sources: OsintSource[]; }

const dsBadge = (ds: OsintSource["dataSource"]) =>
  ds === "real_scraping" ? "REAL" : ds === "precomputed_demo" ? "PRECOMPUTED" : "PROVIDED";

export default function EvidenceTable({ sources }: Props) {
  return (
    <div className="card" style={{ padding: 0, overflow: "hidden" }}>
      <div style={{ padding: "12px 14px", borderBottom: "1px solid var(--color-border)", display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: 14 }}>Evidence table · OSINT triangulation</div>
          <div style={{ fontSize: 11, color: "var(--color-muted)" }}>
            Cada fuente lleva su origen visible. Triangulación mínima ≥ 2 fuentes para validar.
          </div>
        </div>
      </div>
      <table style={{ width: "100%", fontSize: 12, borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#F8FAFC", textAlign: "left" }}>
            {["Source", "Type", "Freshness", "Quality", "Triangulation", "Score", "Status", "Data source"].map((h) => (
              <th key={h} style={{ padding: "8px 10px", color: "var(--color-muted)", fontWeight: 600, fontSize: 11, textTransform: "uppercase", letterSpacing: 0.4 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sources.map((s) => {
            const blocked = s.status === "BLOCKED";
            const lowScore = s.confidenceScore < 60 && !blocked;
            const bg = blocked ? "#FEF2F2" : lowScore ? "#FFFBEB" : "transparent";
            return (
              <tr key={s.id} style={{ borderTop: "1px solid var(--color-border)", background: bg }}>
                <td style={{ padding: "8px 10px", fontWeight: 500 }}>{s.source}</td>
                <td style={{ padding: "8px 10px", color: "var(--color-muted)" }}>{s.type}</td>
                <td style={{ padding: "8px 10px" }}>{s.freshness}</td>
                <td style={{ padding: "8px 10px" }}>{s.quality}</td>
                <td style={{ padding: "8px 10px" }}>{s.triangulation}</td>
                <td style={{ padding: "8px 10px", fontWeight: 700, color: s.confidenceScore >= 70 ? "var(--color-green)" : s.confidenceScore >= 50 ? "var(--color-amber)" : "var(--color-red)" }}>
                  {s.confidenceScore}
                </td>
                <td style={{ padding: "8px 10px" }}>
                  <Badge status={s.status === "VALIDATED" ? "VALIDATED" : s.status === "WARNING" ? "WARNING" : "BLOCKED"} small />
                </td>
                <td style={{ padding: "8px 10px" }}>
                  <Badge status={dsBadge(s.dataSource)} small />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
