import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { campaignKPIs, learningInsights } from "../../data/b2bDemoData";

export default function LearningPanel() {
  return (
    <div className="card" style={{ padding: 16, marginTop: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 10 }}>
        <h3 style={{ fontSize: 14 }}>Learning Engine · KPIs por campaña</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: real_pipeline_output</div>
      </div>
      <div style={{ width: "100%", height: 240 }}>
        <ResponsiveContainer>
          <BarChart data={campaignKPIs} margin={{ top: 10, right: 16, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="campaign" fontSize={11} />
            <YAxis fontSize={11} unit="%" />
            <Tooltip
              formatter={(v: number, n: string) => [`${v.toFixed(1)}%`, n]}
              labelFormatter={(l) => `Campaña: ${l}`}
              contentStyle={{ fontSize: 12 }}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Bar dataKey="open_rate" name="Open rate" fill="#0E7CFF" />
            <Bar dataKey="reply_rate" name="Reply rate" fill="#20C7D9" />
            <Bar dataKey="meeting_rate" name="Meeting rate" fill="#16A34A" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 4 }}>
        Las métricas reportadas son la observación puntual; el motor de aprendizaje compara contra la
        <strong> Wilson lower bound</strong> (95% IC) para evitar conclusiones por azar con muestra pequeña.
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 10, marginTop: 14 }}>
        {learningInsights.map((ins) => (
          <div
            key={ins.id}
            style={{
              border: "1px solid var(--color-border)",
              borderLeft: `4px solid ${ins.confidence >= 0.7 ? "var(--color-green)" : ins.confidence >= 0.5 ? "var(--color-amber)" : "var(--color-red)"}`,
              borderRadius: 6,
              padding: 12,
              fontSize: 12,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
              <span style={{ fontSize: 14 }}>💡</span>
              {ins.references_wilson && (
                <span title="Insight calibrado contra Wilson lower bound" style={{ fontSize: 10, color: "var(--color-muted)", fontWeight: 600, letterSpacing: 0.4, textTransform: "uppercase" }}>
                  Wilson-LB calibrated
                </span>
              )}
              <span style={{ marginLeft: "auto", fontWeight: 700, color: ins.confidence >= 0.7 ? "var(--color-green)" : ins.confidence >= 0.5 ? "var(--color-amber)" : "var(--color-red)" }}>
                {(ins.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div>{ins.text}</div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 18 }}>
        <h3 style={{ fontSize: 14, marginBottom: 8 }}>Why this is agentic</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 10 }}>
          {[
            { i: "🤖", t: "Specialized agents",   d: "Cada fase tiene agentes con un rol único y herramientas propias." },
            { i: "🔀", t: "Conditional decisions", d: "Validator descarta, Classifier asigna cluster, Humanizer reescribe según AI-score." },
            { i: "🔁", t: "Feedback loop",         d: "El LearningEngine condiciona prompts y horarios de la siguiente campaña." },
            { i: "📚", t: "Historical learning",   d: "Memoria persistente entre runs (Wilson LB, ángulos ganadores)." },
            { i: "🛠️", t: "External tools",         d: "SMTP/Resend, IMAP, Google Maps, web scraping, LLM API." },
            { i: "🧠", t: "Persistent memory",     d: "Diagnostics y profiles guardados en disco (data/diagnostics/, phase2_profiles.json)." },
          ].map((c) => (
            <div key={c.t} className="card" style={{ padding: 12 }}>
              <div style={{ fontSize: 18 }}>{c.i}</div>
              <div style={{ fontWeight: 600, fontSize: 12, marginTop: 4 }}>{c.t}</div>
              <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 4 }}>{c.d}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
