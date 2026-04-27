import Badge from "../shared/Badge";
import {
  phase1Counts,
  phase1Sample,
  clusterProfiles,
  classifiedCompanies,
  emailExample,
  followUpExamples,
} from "../../data/b2bDemoData";

interface Props {
  phase: number;
  dryRun: boolean;
  setDryRun: (b: boolean) => void;
}

export default function AgentFlow({ phase, dryRun, setDryRun }: Props) {
  if (phase === 0) return <Phase1 />;
  if (phase === 1) return <Phase2 />;
  if (phase === 2) return <Phase3 dryRun={dryRun} setDryRun={setDryRun} />;
  return <Phase4Placeholder />;
}

function Phase1() {
  const c = phase1Counts;
  const cells: { label: string; n: number; color: string }[] = [
    { label: "Scraped",     n: c.scraped,     color: "#0E7CFF" },
    { label: "Enriched",    n: c.enriched,    color: "#20C7D9" },
    { label: "Valid email", n: c.validEmail,  color: "#16A34A" },
    { label: "No email",    n: c.noEmail,     color: "#F59E0B" },
    { label: "Discarded",   n: c.discarded,   color: "#DC2626" },
  ];
  return (
    <div>
      <PhaseHeader title="Phase 1 · Collection" subtitle="Scraping + enrichment + email validation" dataSource={c.dataSource} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10, marginBottom: 16 }}>
        {cells.map((x) => (
          <div key={x.label} className="card" style={{ padding: 12, textAlign: "center" }}>
            <div style={{ fontSize: 24, fontWeight: 700, color: x.color }}>{x.n}</div>
            <div style={{ fontSize: 11, color: "var(--color-muted)", textTransform: "uppercase", fontWeight: 600 }}>{x.label}</div>
          </div>
        ))}
      </div>
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table style={{ width: "100%", fontSize: 12, borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#F8FAFC", textAlign: "left" }}>
              {["Company", "Domain", "City", "Sector", "Size", "Email", "Status"].map((h) => (
                <th key={h} style={{ padding: "8px 10px", color: "var(--color-muted)", fontWeight: 600, fontSize: 11, textTransform: "uppercase", letterSpacing: 0.4 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {phase1Sample.map((c) => (
              <tr key={c.id} style={{ borderTop: "1px solid var(--color-border)" }}>
                <td style={{ padding: "8px 10px", fontWeight: 500 }}>{c.name}</td>
                <td style={{ padding: "8px 10px", color: "var(--color-muted)" }}>{c.domain}</td>
                <td style={{ padding: "8px 10px" }}>{c.city}</td>
                <td style={{ padding: "8px 10px" }}>{c.sector}</td>
                <td style={{ padding: "8px 10px" }}>{c.size}</td>
                <td style={{ padding: "8px 10px" }} className="mono">{c.email ?? "—"}</td>
                <td style={{ padding: "8px 10px" }}>
                  <Badge status={c.status === "valid" ? "VALIDATED" : c.status === "no_email" ? "WARNING" : "BLOCKED"} small>
                    {c.status}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Phase2() {
  return (
    <div>
      <PhaseHeader title="Phase 2 · Intelligence" subtitle="Clustering + scoring + cluster profiles" dataSource="real_pipeline_output" />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 12, marginBottom: 16 }}>
        {clusterProfiles.map((p) => (
          <div key={p.cluster_id} className="card" style={{ padding: 14, borderTop: p.unclassifiable ? "3px solid #94a3b8" : "3px solid var(--color-blue)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
              <div style={{ fontWeight: 700, fontSize: 13 }}>Cluster {p.cluster_id}</div>
              {p.unclassifiable ? <Badge status="UNCLASSIFIABLE" /> : <Badge status="VALIDATED" small>{p.tone}</Badge>}
            </div>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>{p.label}</div>
            <div style={{ fontSize: 11, color: "var(--color-muted)" }}>
              {p.primary_sector} · {p.avg_size} · score avg {p.avg_score} · {p.company_count} empresas
            </div>
            <div style={{ marginTop: 8, fontSize: 12 }}>
              <div style={{ color: "var(--color-muted)", fontSize: 10, textTransform: "uppercase", letterSpacing: 0.4, fontWeight: 600 }}>Pain</div>
              <div>{p.key_pain}</div>
            </div>
            <div style={{ marginTop: 6, fontSize: 12 }}>
              <div style={{ color: "var(--color-muted)", fontSize: 10, textTransform: "uppercase", letterSpacing: 0.4, fontWeight: 600 }}>Value prop</div>
              <div>{p.value_prop}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table style={{ width: "100%", fontSize: 12, borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#F8FAFC", textAlign: "left" }}>
              {["Company", "Cluster", "Sector confidence", "Lead score"].map((h) => (
                <th key={h} style={{ padding: "8px 10px", color: "var(--color-muted)", fontWeight: 600, fontSize: 11, textTransform: "uppercase", letterSpacing: 0.4 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {classifiedCompanies.map((c) => (
              <tr key={c.id} style={{ borderTop: "1px solid var(--color-border)" }}>
                <td style={{ padding: "8px 10px" }}>{c.name}</td>
                <td style={{ padding: "8px 10px", fontWeight: 600 }}>{c.cluster_id === -1 ? "—" : c.cluster_id}</td>
                <td style={{ padding: "8px 10px" }}>{(c.sector_confidence * 100).toFixed(0)}%</td>
                <td style={{ padding: "8px 10px", fontWeight: 700, color: c.lead_score >= 70 ? "var(--color-green)" : c.lead_score >= 50 ? "var(--color-amber)" : "var(--color-red)" }}>{c.lead_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Phase3({ dryRun, setDryRun }: { dryRun: boolean; setDryRun: (b: boolean) => void }) {
  const e = emailExample;
  return (
    <div>
      <PhaseHeader title="Phase 3 · Outreach" subtitle="Copywriter + Humanizer + Sender + Follow-up" dataSource="real_pipeline_output" />

      <div className="card" style={{ padding: 14, marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ fontWeight: 600, fontSize: 13 }}>dry_run mode</div>
          <button
            onClick={() => setDryRun(!dryRun)}
            style={{
              border: 0,
              background: dryRun ? "var(--color-green)" : "var(--color-red)",
              color: "#fff",
              padding: "4px 12px",
              borderRadius: 999,
              fontWeight: 700,
              fontSize: 11,
              cursor: "pointer",
            }}
          >
            {dryRun ? "ON" : "OFF"}
          </button>
          <span style={{ fontSize: 12, color: "var(--color-muted)" }}>
            Cuando ON, los emails se previsualizan pero no se envían.
          </span>
        </div>
        {!dryRun && (
          <div style={{ marginTop: 10, padding: 10, background: "#FEF2F2", border: "1px solid #FECACA", borderRadius: 6, fontSize: 12 }}>
            ⚠ Live mode would send real emails via Resend API. <strong>In this demo, dry_run is ON by default.</strong> El front
            no llama a ningún endpoint real; este toggle es solo ilustrativo.
          </div>
        )}
      </div>

      <div className="card" style={{ padding: 14, marginBottom: 12 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <div>
            <div style={{ fontWeight: 600, fontSize: 13 }}>Email · {e.recipient_company}</div>
            <div style={{ fontSize: 11, color: "var(--color-muted)" }}>
              to {e.recipient} · cluster {e.cluster_id} · sequence_step {e.sequence_step}
            </div>
          </div>
          <Badge status="REAL" small>real_pipeline_output</Badge>
        </div>
        <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 8 }}>Subject: {e.subject}</div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
          <div>
            <div style={{ fontSize: 10, color: "var(--color-muted)", textTransform: "uppercase", fontWeight: 700, letterSpacing: 0.4, marginBottom: 4 }}>Before humanizer</div>
            <pre style={{ background: "#F8FAFC", border: "1px solid var(--color-border)", borderRadius: 6, padding: 10, whiteSpace: "pre-wrap", fontSize: 12, fontFamily: "Inter, system-ui, sans-serif", margin: 0 }}>
              <DiffText text={e.before_humanizer} flagged={["exhaustivamente", "significativamente", "considerable", "inherente", "Estimados señores", "Reciba un cordial saludo"]} />
            </pre>
          </div>
          <div>
            <div style={{ fontSize: 10, color: "var(--color-muted)", textTransform: "uppercase", fontWeight: 700, letterSpacing: 0.4, marginBottom: 4 }}>After humanizer</div>
            <pre style={{ background: "#F0FDF4", border: "1px solid #BBF7D0", borderRadius: 6, padding: 10, whiteSpace: "pre-wrap", fontSize: 12, fontFamily: "Inter, system-ui, sans-serif", margin: 0 }}>
              {e.after_humanizer}
            </pre>
          </div>
        </div>
        <div style={{ marginTop: 8, fontSize: 11, color: "var(--color-muted)", fontStyle: "italic" }}>
          HumanizerAgent removed AI-like phrasing (formal openings, intensifiers, triadic structures); compactó párrafos y dejó un único CTA concreto.
        </div>
      </div>

      <div className="card" style={{ padding: 14 }}>
        <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 8 }}>Follow-up scheduled (sequence_step 1)</div>
        <div style={{ fontSize: 12, padding: 10, background: "#F8FAFC", borderRadius: 6, border: "1px solid var(--color-border)" }}>
          {followUpExamples[0].after_humanizer}
        </div>
        <div style={{ marginTop: 6, fontSize: 11, color: "var(--color-muted)" }}>source: simulated_realistic · enviado a +72h si no hay reply</div>
      </div>
    </div>
  );
}

function Phase4Placeholder() {
  return (
    <div>
      <PhaseHeader title="Phase 4 · Learning" subtitle="Wilson lower bounds + insight memory" dataSource="real_pipeline_output" />
      <div className="card" style={{ padding: 14 }}>
        <div style={{ fontSize: 13 }}>
          La salida de aprendizaje (KPIs por campaña + insights) se muestra en el panel inferior.
          Esta fase actualiza la memoria persistente del orquestador para condicionar la siguiente ejecución.
        </div>
      </div>
    </div>
  );
}

function PhaseHeader({ title, subtitle, dataSource }: { title: string; subtitle: string; dataSource: string }) {
  return (
    <div style={{ marginBottom: 12, display: "flex", alignItems: "baseline", justifyContent: "space-between" }}>
      <div>
        <h3 style={{ fontSize: 15 }}>{title}</h3>
        <div style={{ fontSize: 12, color: "var(--color-muted)" }}>{subtitle}</div>
      </div>
      <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: {dataSource}</div>
    </div>
  );
}

function DiffText({ text, flagged }: { text: string; flagged: string[] }) {
  let out: Array<{ s: string; flag: boolean }> = [{ s: text, flag: false }];
  flagged.forEach((f) => {
    const next: typeof out = [];
    out.forEach((seg) => {
      if (seg.flag) { next.push(seg); return; }
      const parts = seg.s.split(f);
      parts.forEach((p, i) => {
        next.push({ s: p, flag: false });
        if (i < parts.length - 1) next.push({ s: f, flag: true });
      });
    });
    out = next;
  });
  return (
    <>
      {out.map((seg, i) =>
        seg.flag ? (
          <mark key={i} style={{ background: "#FEF3C7", color: "#92400E", padding: "0 2px", borderRadius: 3 }}>{seg.s}</mark>
        ) : (
          <span key={i}>{seg.s}</span>
        )
      )}
    </>
  );
}
