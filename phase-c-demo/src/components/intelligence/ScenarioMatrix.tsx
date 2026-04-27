import { useState } from "react";
import Badge from "../shared/Badge";
import type { Scenario } from "../../types/intelligence";

interface Props { scenarios: Scenario[]; }

export default function ScenarioMatrix({ scenarios }: Props) {
  const [selected, setSelected] = useState<string | null>("E3");

  const cell = (xLabel: "low" | "high", yLabel: "low" | "high") => {
    const s = scenarios.find((x) => x.quadrant.x === xLabel && x.quadrant.y === yLabel)!;
    const isSelected = selected === s.id;
    return (
      <button
        key={s.id}
        onClick={() => setSelected(s.id === selected ? null : s.id)}
        style={{
          textAlign: "left",
          padding: 14,
          background: isSelected ? "#FFFBEB" : "#fff",
          border: s.dominant ? "2px solid var(--color-amber)" : "1px solid var(--color-border)",
          borderRadius: 8,
          cursor: "pointer",
          minHeight: 140,
          position: "relative",
        }}
      >
        {s.dominant && (
          <div style={{ position: "absolute", top: 8, right: 8 }}>
            <Badge status="DOMINANT" small />
          </div>
        )}
        <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 700, letterSpacing: 0.5 }}>{s.id}</div>
        <div style={{ fontWeight: 600, fontSize: 13, marginTop: 4 }}>{s.title.replace(/^E\d+ · /, "")}</div>
        <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 6 }}>
          {s.quadrant.x === "high" ? "↑" : "↓"} inversión · {s.quadrant.y === "high" ? "↑" : "↓"} conversión
        </div>
      </button>
    );
  };

  const expanded = scenarios.find((s) => s.id === selected);

  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 10 }}>
        <h3 style={{ fontSize: 14 }}>Scenario matrix · 2×2</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: precomputed_demo</div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "60px 1fr 1fr", gap: 8 }}>
        <div style={{ writingMode: "vertical-rl", transform: "rotate(180deg)", textAlign: "center", fontSize: 11, color: "var(--color-muted)", fontWeight: 600 }}>
          Conversión ↑ &nbsp; · &nbsp; ↓
        </div>
        <div>{cell("low", "high")}</div>
        <div>{cell("high", "high")}</div>
        <div></div>
        <div>{cell("low", "low")}</div>
        <div>{cell("high", "low")}</div>
        <div></div>
        <div style={{ textAlign: "center", fontSize: 11, color: "var(--color-muted)", fontWeight: 600, gridColumn: "2 / span 2" }}>
          ← Inversión publicitaria →
        </div>
      </div>

      {expanded && (
        <div style={{ marginTop: 14, padding: 14, background: "#F8FAFC", borderRadius: 6, border: "1px solid var(--color-border)" }}>
          <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 8 }}>{expanded.title}</div>
          <div style={{ fontSize: 11, fontWeight: 700, color: "var(--color-muted)", textTransform: "uppercase", letterSpacing: 0.4 }}>Signposts</div>
          <ul style={{ marginTop: 4, paddingLeft: 18, fontSize: 12 }}>
            {expanded.signposts.map((sp, i) => <li key={i}>{sp}</li>)}
          </ul>
          <div style={{ marginTop: 10, fontSize: 11, fontWeight: 700, color: "var(--color-muted)", textTransform: "uppercase", letterSpacing: 0.4 }}>Decisión</div>
          <div style={{ fontSize: 13, fontWeight: 500, marginTop: 4 }}>{expanded.decision}</div>
        </div>
      )}
    </div>
  );
}
