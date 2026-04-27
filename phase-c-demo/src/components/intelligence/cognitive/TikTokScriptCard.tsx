import type { TikTokScript } from "../../../data/extendedData";

interface Props { script: TikTokScript; }

export default function TikTokScriptCard({ script: s }: Props) {
  return (
    <div className="card" style={{ padding: 0, overflow: "hidden", display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", padding: "10px 12px", background: "#0F172A", color: "#fff", alignItems: "center", gap: 8 }}>
        <span style={{ fontSize: 14 }}>🎬</span>
        <span style={{ fontWeight: 700, fontSize: 11, letterSpacing: 0.5, textTransform: "uppercase" }}>TikTok</span>
        <span style={{ fontSize: 11, color: "#94a3b8" }}>· {s.day} · {s.slot} · {s.duration}</span>
        <span style={{ marginLeft: "auto", fontSize: 10, color: "#20C7D9", fontFamily: "monospace" }}>{s.id}</span>
      </div>
      <div style={{ padding: 14, flex: 1, display: "flex", flexDirection: "column" }}>
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 8 }}>{s.title}</div>

        <div style={{ background: "#FEF3C7", padding: 8, borderRadius: 4, fontSize: 12, fontStyle: "italic", marginBottom: 10, borderLeft: "3px solid #F59E0B" }}>
          🎯 <strong>Hook (0–3s):</strong> {s.hook}
        </div>

        <div style={{ fontSize: 11, fontWeight: 700, color: "var(--color-muted)", textTransform: "uppercase", letterSpacing: 0.4, marginBottom: 4 }}>Beats</div>
        <ol style={{ paddingLeft: 20, marginTop: 0, marginBottom: 10, fontSize: 12 }}>
          {s.beats.map((b, i) => <li key={i} style={{ marginBottom: 2 }}>{b}</li>)}
        </ol>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 10 }}>
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--color-muted)", textTransform: "uppercase", letterSpacing: 0.4 }}>CTA</div>
            <div style={{ fontSize: 12 }}>{s.cta}</div>
          </div>
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--color-muted)", textTransform: "uppercase", letterSpacing: 0.4 }}>Música</div>
            <div style={{ fontSize: 12 }}>{s.music}</div>
          </div>
        </div>

        <div style={{ marginBottom: 10 }}>
          {s.hashtags.map((h) => (
            <span key={h} style={{ display: "inline-block", background: "#EFF6FF", color: "#0E7CFF", padding: "2px 8px", borderRadius: 999, fontSize: 11, fontWeight: 500, marginRight: 4, marginBottom: 4 }}>{h}</span>
          ))}
        </div>

        <div style={{ marginTop: "auto", paddingTop: 10, borderTop: "1px dashed var(--color-border)" }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: "var(--color-blue)", textTransform: "uppercase", letterSpacing: 0.4 }}>
            Por qué para Nauta
          </div>
          <div style={{ fontSize: 12, marginTop: 4, color: "var(--color-text)" }}>{s.rationale}</div>
          <div style={{ fontSize: 10, fontStyle: "italic", color: "var(--color-muted)", marginTop: 6 }}>
            ↳ origen: {s.sourceLink}
          </div>
        </div>
      </div>
    </div>
  );
}
