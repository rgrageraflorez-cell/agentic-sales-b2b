import { osintGraph } from "../../../data/extendedData";

const GROUP_COLOR: Record<string, string> = {
  core:     "#0B1F3A",
  official: "#4338CA",
  social:   "#0E7CFF",
  press:    "#16A34A",
  industry: "#A855F7",
  blocked:  "#DC2626",
};

export default function OsintGraph() {
  const W = 720, H = 320;
  const cx = W / 2, cy = H / 2;
  const periphery = osintGraph.nodes.filter((n) => n.id !== "claim");
  const angle = (i: number) => (i / periphery.length) * Math.PI * 2 - Math.PI / 2;
  const positions: Record<string, { x: number; y: number }> = { claim: { x: cx, y: cy } };
  periphery.forEach((n, i) => {
    const a = angle(i);
    positions[n.id] = { x: cx + Math.cos(a) * 220, y: cy + Math.sin(a) * 120 };
  });

  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <h3 style={{ fontSize: 14 }}>Grafo OSINT · triangulación de fuentes</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: mixed</div>
      </div>
      <div style={{ width: "100%", overflowX: "auto" }}>
        <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H} style={{ minWidth: 600 }}>
          {osintGraph.edges.map((e, i) => {
            const a = positions[e.from], b = positions[e.to];
            const node = osintGraph.nodes.find((n) => n.id === e.to)!;
            const blocked = node.group === "blocked";
            return (
              <line
                key={i}
                x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                stroke={blocked ? "#DC2626" : "#94a3b8"}
                strokeWidth={blocked ? 1.2 : 1 + e.weight * 2.5}
                strokeDasharray={blocked ? "4 4" : "0"}
                opacity={blocked ? 0.8 : 0.6}
              />
            );
          })}
          {osintGraph.nodes.map((n) => {
            const p = positions[n.id];
            const r = n.id === "claim" ? 56 : 42;
            const color = GROUP_COLOR[n.group];
            return (
              <g key={n.id}>
                <circle cx={p.x} cy={p.y} r={r} fill="#fff" stroke={color} strokeWidth={n.id === "claim" ? 3 : 2} />
                <text x={p.x} y={p.y - 6} textAnchor="middle" fontSize={n.id === "claim" ? 10 : 9} fontWeight={700} fill={color}>
                  {wrap(n.label, 16).map((line, i) => (
                    <tspan key={i} x={p.x} dy={i === 0 ? 0 : 11}>{line}</tspan>
                  ))}
                </text>
                <text x={p.x} y={p.y + r - 8} textAnchor="middle" fontSize={9} fontWeight={700} fill={n.score >= 70 ? "#16A34A" : n.score >= 50 ? "#F59E0B" : "#DC2626"}>
                  {n.score}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 8, fontSize: 11 }}>
        {Object.entries(GROUP_COLOR).map(([g, c]) => (
          <div key={g} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ width: 10, height: 10, borderRadius: "50%", background: c, display: "inline-block" }} />
            <span style={{ color: "var(--color-muted)" }}>{g}</span>
          </div>
        ))}
      </div>
      <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 4 }}>
        El nodo central es la hipótesis. El borde rojo punteado al "Foro NáuticaPro" indica fuente bloqueada (no triangula).
      </div>
    </div>
  );
}

function wrap(text: string, max: number): string[] {
  const words = text.split(" ");
  const lines: string[] = [];
  let cur = "";
  for (const w of words) {
    if ((cur + " " + w).trim().length > max) {
      if (cur) lines.push(cur);
      cur = w;
    } else cur = (cur + " " + w).trim();
  }
  if (cur) lines.push(cur);
  return lines.slice(0, 3);
}
