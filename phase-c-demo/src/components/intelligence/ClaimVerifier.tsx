import Badge from "../shared/Badge";
import type { Claim } from "../../types/intelligence";

interface Props { claims: Claim[]; }

export default function ClaimVerifier({ claims }: Props) {
  return (
    <div className="card" style={{ padding: 0, overflow: "hidden" }}>
      <div style={{ padding: "12px 14px", borderBottom: "1px solid var(--color-border)", display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: 14 }}>Claim Verifier</div>
          <div style={{ fontSize: 11, color: "var(--color-muted)" }}>
            Bloquea afirmaciones causales o predictivas sin evidencia suficiente.
          </div>
        </div>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: precomputed_demo</div>
      </div>
      <table style={{ width: "100%", fontSize: 12, borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#F8FAFC", textAlign: "left" }}>
            {["Claim", "Type", "Source", "Status", "Reason"].map((h) => (
              <th key={h} style={{ padding: "8px 10px", color: "var(--color-muted)", fontWeight: 600, fontSize: 11, textTransform: "uppercase", letterSpacing: 0.4 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {claims.map((c) => {
            const blocked = c.status === "BLOCKED";
            return (
              <tr key={c.id} style={{ borderTop: "1px solid var(--color-border)", background: blocked ? "#FEF2F2" : "#F0FDF4" }}>
                <td style={{ padding: "10px", maxWidth: 360 }}>
                  <span style={{ marginRight: 6 }}>{blocked ? "🔒" : "✓"}</span>
                  {c.text}
                </td>
                <td style={{ padding: "10px", color: "var(--color-muted)" }}>{c.type}</td>
                <td style={{ padding: "10px", color: "var(--color-muted)" }}>{c.source}</td>
                <td style={{ padding: "10px" }}>
                  <Badge status={blocked ? "BLOCKED" : "APPROVED"} small />
                </td>
                <td style={{ padding: "10px", color: blocked ? "#7F1D1D" : "var(--color-text)", maxWidth: 280 }}>{c.reason}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
