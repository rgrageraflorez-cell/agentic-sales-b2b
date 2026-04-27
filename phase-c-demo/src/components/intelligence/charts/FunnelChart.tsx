import { funnelData } from "../../../data/extendedData";

export default function FunnelChart() {
  const max = Math.max(...funnelData.map((s) => s.count));
  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <h3 style={{ fontSize: 14 }}>Funnel de checkout · febrero vs benchmark sectorial</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: provided_report</div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {funnelData.map((s, i) => {
          const widthPct = (s.count / max) * 100;
          const drop = i > 0 ? funnelData[i - 1].count - s.count : 0;
          const dropPct = i > 0 ? ((drop / funnelData[i - 1].count) * 100).toFixed(0) : null;
          const benchmarkGap = s.benchmark_pct - s.conversion_pct;
          const isCritical = i > 0 && benchmarkGap > 15;
          return (
            <div key={s.step}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ minWidth: 160, fontSize: 12, fontWeight: 500 }}>{s.step}</div>
                <div style={{ flex: 1, height: 26, background: "#F1F5F9", borderRadius: 4, position: "relative", overflow: "hidden" }}>
                  <div
                    style={{
                      width: `${widthPct}%`,
                      height: "100%",
                      background: isCritical ? "linear-gradient(90deg, #DC2626, #F87171)" : "linear-gradient(90deg, #0E7CFF, #20C7D9)",
                      transition: "width 400ms",
                      display: "flex",
                      alignItems: "center",
                      paddingLeft: 8,
                      color: "#fff",
                      fontWeight: 600,
                      fontSize: 12,
                    }}
                  >
                    {s.count.toLocaleString("es-ES")}
                  </div>
                </div>
                <div style={{ minWidth: 78, textAlign: "right", fontSize: 11 }}>
                  <span style={{ fontWeight: 700, color: isCritical ? "var(--color-red)" : "var(--color-text)" }}>
                    {s.conversion_pct.toFixed(1)}%
                  </span>
                  <span style={{ color: "var(--color-muted)" }}> / {s.benchmark_pct}%</span>
                </div>
              </div>
              {dropPct && (
                <div style={{ marginLeft: 168, fontSize: 10, color: isCritical ? "var(--color-red)" : "var(--color-muted)", fontStyle: "italic", marginTop: 2 }}>
                  ↓ {dropPct}% drop ({drop.toLocaleString("es-ES")} usuarios) · benchmark esperaba dejar caer {(100 - s.benchmark_pct).toFixed(0)}%
                </div>
              )}
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 14, padding: 10, background: "#FEF2F2", border: "1px solid #FECACA", borderRadius: 6, fontSize: 12 }}>
        ⚠ <strong>Cuello de botella detectado:</strong> entre "Inicio de checkout" y "Pago iniciado" se pierde el 65% (benchmark sectorial: 22%). Diferencial de 43 puntos sugiere fricción en el formulario de pago — alineado con la hipótesis OSINT.
      </div>
    </div>
  );
}
