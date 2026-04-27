import type { ConfidenceIndex } from "../../types/intelligence";

interface Props { ci: ConfidenceIndex; }

export default function ConfidencePanel({ ci }: Props) {
  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 10 }}>
        <h3 style={{ fontSize: 14 }}>Índice de confianza · breakdown</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: precomputed_demo</div>
      </div>
      <table style={{ width: "100%", fontSize: 13, borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#F8FAFC", textAlign: "left" }}>
            {["Componente", "Peso", "Score", "Contribución"].map((h) => (
              <th key={h} style={{ padding: "8px 10px", color: "var(--color-muted)", fontWeight: 600, fontSize: 11, textTransform: "uppercase", letterSpacing: 0.4 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ci.breakdown.map((b) => (
            <tr key={b.component} style={{ borderTop: "1px solid var(--color-border)" }}>
              <td style={{ padding: "8px 10px", fontWeight: 500 }}>{b.component}</td>
              <td style={{ padding: "8px 10px" }}>{b.weight.toFixed(2)}</td>
              <td style={{ padding: "8px 10px" }}>{b.score.toFixed(2)}</td>
              <td style={{ padding: "8px 10px", fontWeight: 600 }}>{b.contribution.toFixed(3)}</td>
            </tr>
          ))}
          <tr style={{ borderTop: "2px solid var(--color-text)", background: "#F8FAFC" }}>
            <td style={{ padding: "10px", fontWeight: 700 }}>Final index</td>
            <td style={{ padding: "10px" }}>—</td>
            <td style={{ padding: "10px" }}>—</td>
            <td style={{ padding: "10px", fontWeight: 700, color: ci.finalIndex >= 0.7 ? "var(--color-green)" : ci.finalIndex >= ci.threshold ? "var(--color-amber)" : "var(--color-red)" }}>
              {ci.finalIndex.toFixed(2)}
            </td>
          </tr>
        </tbody>
      </table>
      <div style={{ marginTop: 8, fontSize: 11, color: "var(--color-muted)" }}>
        Modo actual: <strong>{ci.mode}</strong>. Umbral mínimo para emitir conclusiones: {ci.threshold.toFixed(2)}.
      </div>
    </div>
  );
}
