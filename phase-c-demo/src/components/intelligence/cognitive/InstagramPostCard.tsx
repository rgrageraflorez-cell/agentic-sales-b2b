import type { InstagramPost } from "../../../data/extendedData";

interface Props { post: InstagramPost; }

const FORMAT_COLOR: Record<InstagramPost["format"], string> = {
  Reel: "#E1306C",
  Carrusel: "#0E7CFF",
  Story: "#F59E0B",
  "Post estático": "#16A34A",
};

export default function InstagramPostCard({ post: p }: Props) {
  const color = FORMAT_COLOR[p.format];
  return (
    <div className="card" style={{ padding: 0, overflow: "hidden", display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", padding: "10px 12px", background: "linear-gradient(135deg, #833AB4, #E1306C, #F77737)", color: "#fff", alignItems: "center", gap: 8 }}>
        <span style={{ fontSize: 14 }}>📸</span>
        <span style={{ fontWeight: 700, fontSize: 11, letterSpacing: 0.5, textTransform: "uppercase" }}>Instagram · {p.format}</span>
        <span style={{ fontSize: 11, color: "rgba(255,255,255,0.85)" }}>· {p.day} · {p.slot}</span>
        <span style={{ marginLeft: "auto", fontSize: 10, fontFamily: "monospace", color: "rgba(255,255,255,0.7)" }}>{p.id}</span>
      </div>

      <div style={{ padding: 14, flex: 1, display: "flex", flexDirection: "column" }}>
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 8 }}>{p.hook}</div>

        <div style={{ fontSize: 11, fontWeight: 700, color: "var(--color-muted)", textTransform: "uppercase", letterSpacing: 0.4, marginBottom: 4 }}>
          Imagen / formato
        </div>
        <div style={{ background: "#F8FAFC", padding: 10, borderRadius: 4, fontSize: 12, marginBottom: 10, border: `1px dashed ${color}` }}>
          🖼️ {p.imageIdea}
        </div>

        <div style={{ fontSize: 11, fontWeight: 700, color: "var(--color-muted)", textTransform: "uppercase", letterSpacing: 0.4, marginBottom: 4 }}>
          Caption
        </div>
        <div style={{ fontSize: 12, whiteSpace: "pre-wrap", marginBottom: 10, padding: 10, background: "#fff", border: "1px solid var(--color-border)", borderRadius: 4 }}>
          {p.caption}
        </div>

        {p.hashtags.length > 0 && (
          <div style={{ marginBottom: 10 }}>
            {p.hashtags.map((h) => (
              <span key={h} style={{ display: "inline-block", background: "#FCE7F3", color: "#BE185D", padding: "2px 8px", borderRadius: 999, fontSize: 11, fontWeight: 500, marginRight: 4, marginBottom: 4 }}>{h}</span>
            ))}
          </div>
        )}

        <div style={{ marginTop: "auto", paddingTop: 10, borderTop: "1px dashed var(--color-border)" }}>
          <div style={{ fontSize: 10, fontWeight: 700, color, textTransform: "uppercase", letterSpacing: 0.4 }}>
            Por qué para Nauta
          </div>
          <div style={{ fontSize: 12, marginTop: 4 }}>{p.rationale}</div>
        </div>
      </div>
    </div>
  );
}
