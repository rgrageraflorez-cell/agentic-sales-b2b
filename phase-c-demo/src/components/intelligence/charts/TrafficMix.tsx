import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { trafficSources } from "../../../data/extendedData";

export default function TrafficMix() {
  const total = trafficSources.reduce((a, b) => a + b.sessions, 0);
  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <h3 style={{ fontSize: 14 }}>Mix de tráfico · sesiones y conversión por canal</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: provided_report</div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", gap: 14, alignItems: "center" }}>
        <div style={{ width: 200, height: 200 }}>
          <ResponsiveContainer>
            <PieChart>
              <Pie data={trafficSources} dataKey="sessions" nameKey="source" innerRadius={50} outerRadius={90} paddingAngle={2}>
                {trafficSources.map((s, i) => <Cell key={i} fill={s.color} />)}
              </Pie>
              <Tooltip formatter={(v: number, _n, p: { payload?: { source?: string } }) => [`${v.toLocaleString("es-ES")} sesiones`, p?.payload?.source ?? ""]} contentStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div>
          <table style={{ width: "100%", fontSize: 12, borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#F8FAFC", textAlign: "left" }}>
                {["Canal", "Sesiones", "% mix", "CR", "CPA", "Δ MoM"].map((h) => (
                  <th key={h} style={{ padding: "6px 8px", color: "var(--color-muted)", fontWeight: 600, fontSize: 10, textTransform: "uppercase", letterSpacing: 0.4 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {trafficSources.map((s) => (
                <tr key={s.source} style={{ borderTop: "1px solid var(--color-border)" }}>
                  <td style={{ padding: "6px 8px" }}>
                    <span style={{ display: "inline-block", width: 10, height: 10, background: s.color, borderRadius: 2, marginRight: 6 }} />
                    {s.source}
                  </td>
                  <td style={{ padding: "6px 8px" }}>{s.sessions.toLocaleString("es-ES")}</td>
                  <td style={{ padding: "6px 8px" }}>{((s.sessions / total) * 100).toFixed(0)}%</td>
                  <td style={{ padding: "6px 8px", fontWeight: 600, color: s.conversion >= 1.5 ? "var(--color-green)" : s.conversion >= 1 ? "var(--color-amber)" : "var(--color-red)" }}>{s.conversion.toFixed(2)}%</td>
                  <td style={{ padding: "6px 8px" }}>{s.cpa > 0 ? `${s.cpa.toFixed(2)}€` : "—"}</td>
                  <td style={{ padding: "6px 8px", color: s.delta.startsWith("+") ? "var(--color-green)" : "var(--color-red)", fontWeight: 600 }}>{s.delta}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <div style={{ marginTop: 10, padding: 10, background: "#FFFBEB", border: "1px solid #FDE68A", borderRadius: 6, fontSize: 12 }}>
        💡 <strong>Lectura:</strong> el canal de pago crece en sesiones (+18%) pero su conversión es la <em>peor</em> (0.78%). Cada euro adicional en publicidad llega a un funnel roto. Refuerza la decisión E3 (auditar antes de escalar).
      </div>
    </div>
  );
}
