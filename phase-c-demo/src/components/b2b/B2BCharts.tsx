import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import {
  leadFunnel,
  sequencePerformance,
  geoDistribution,
  humanizerScores,
} from "../../data/extendedData";

export function LeadFunnelChart() {
  const max = leadFunnel[0].n;
  return (
    <div className="card" style={{ padding: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <h3 style={{ fontSize: 14 }}>Funnel de leads · run actual</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: real_pipeline_output</div>
      </div>
      <div>
        {leadFunnel.map((s, i) => {
          const pct = (s.n / max) * 100;
          const dropPct = i > 0 ? Math.round(((leadFunnel[i - 1].n - s.n) / leadFunnel[i - 1].n) * 100) : 0;
          return (
            <div key={s.step} style={{ marginBottom: 8 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ minWidth: 130, fontSize: 12, fontWeight: 500 }}>{s.step}</div>
                <div style={{ flex: 1, height: 22, background: "#F1F5F9", borderRadius: 4, overflow: "hidden" }}>
                  <div style={{ width: `${pct}%`, height: "100%", background: "linear-gradient(90deg, #0E7CFF, #20C7D9)", display: "flex", alignItems: "center", paddingLeft: 8, color: "#fff", fontSize: 11, fontWeight: 600 }}>
                    {s.n}
                  </div>
                </div>
                <div style={{ minWidth: 50, textAlign: "right", fontSize: 11, color: "var(--color-muted)" }}>
                  {i > 0 && `-${dropPct}%`}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 6 }}>
        25 → 1 = 4% de conversión a meeting. El cuello principal está en open → reply (37,5% → 18,8% del paso anterior).
      </div>
    </div>
  );
}

export function SequencePerformanceChart() {
  return (
    <div className="card" style={{ padding: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <h3 style={{ fontSize: 14 }}>Rendimiento por paso de secuencia</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: simulated_realistic</div>
      </div>
      <div style={{ width: "100%", height: 220 }}>
        <ResponsiveContainer>
          <BarChart data={sequencePerformance} margin={{ top: 6, right: 16, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="label" fontSize={11} />
            <YAxis fontSize={11} unit="%" />
            <Tooltip contentStyle={{ fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Bar dataKey="open_rate"    name="Open"    fill="#0E7CFF" />
            <Bar dataKey="reply_rate"   name="Reply"   fill="#20C7D9" />
            <Bar dataKey="meeting_rate" name="Meeting" fill="#16A34A" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 4 }}>
        El primer email es el que más rinde; cada follow-up degrada ~25% open y ~45% reply. Datos usados por el LearningEngine para limitar follow-ups a 3.
      </div>
    </div>
  );
}

export function GeoChart() {
  const max = Math.max(...geoDistribution.map((g) => g.n));
  return (
    <div className="card" style={{ padding: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <h3 style={{ fontSize: 14 }}>Distribución geográfica de leads</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: real_pipeline_output</div>
      </div>
      <div>
        {geoDistribution.map((g) => (
          <div key={g.city} style={{ display: "flex", alignItems: "center", gap: 8, padding: "4px 0", fontSize: 12 }}>
            <div style={{ minWidth: 100, fontWeight: 500 }}>📍 {g.city}</div>
            <div style={{ flex: 1, height: 14, background: "#F1F5F9", borderRadius: 4, overflow: "hidden" }}>
              <div style={{ width: `${(g.n / max) * 100}%`, height: "100%", background: "#0E7CFF" }} />
            </div>
            <div style={{ minWidth: 40, textAlign: "right", fontWeight: 700 }}>{g.n}</div>
            <div style={{ minWidth: 130, color: "var(--color-muted)", fontSize: 11 }}>{g.sector}</div>
          </div>
        ))}
      </div>
      <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 6 }}>
        Concentración Madrid (36%) · Cataluña + Valencia (28%) · resto distribuido. Coincide con la base de tiendas físicas de fotografía en España.
      </div>
    </div>
  );
}

export function HumanizerScoreChart() {
  return (
    <div className="card" style={{ padding: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <h3 style={{ fontSize: 14 }}>HumanizerAgent · AI-score antes / después</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: real_pipeline_output</div>
      </div>
      <div style={{ width: "100%", height: 200 }}>
        <ResponsiveContainer>
          <LineChart data={humanizerScores} margin={{ top: 6, right: 16, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="batch" fontSize={11} />
            <YAxis fontSize={11} unit="" domain={[0, 100]} />
            <Tooltip contentStyle={{ fontSize: 12 }} formatter={(v: number) => [`${v} / 100`, ""]} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line type="monotone" dataKey="before" name="Antes" stroke="#DC2626" strokeWidth={2} dot />
            <Line type="monotone" dataKey="after"  name="Después" stroke="#16A34A" strokeWidth={2} dot />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 4 }}>
        AI-score ≈ probabilidad de detectarse como IA (0 = humano, 100 = IA evidente). El humanizer baja el score un 60–70% por lote.
      </div>
    </div>
  );
}
