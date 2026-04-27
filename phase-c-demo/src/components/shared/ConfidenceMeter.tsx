interface Props {
  score: number; // 0–100
  label: string;
  mode: "FULL" | "LIMITED" | "SILENCE";
}

export default function ConfidenceMeter({ score, label, mode }: Props) {
  const color = score >= 70 ? "var(--color-green)" : score >= 50 ? "var(--color-amber)" : "var(--color-red)";
  const modeColor = mode === "FULL" ? "var(--color-green)" : mode === "LIMITED" ? "var(--color-amber)" : "var(--color-red)";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, flex: 1 }}>
      <div style={{ minWidth: 110, fontSize: 12, color: "var(--color-muted)", fontWeight: 600 }}>{label}</div>
      <div style={{ flex: 1, height: 8, background: "#E2E8F0", borderRadius: 999, position: "relative", overflow: "hidden" }}>
        <div
          style={{
            width: `${Math.max(0, Math.min(100, score))}%`,
            height: "100%",
            background: color,
            transition: "width 400ms ease, background 400ms ease",
          }}
        />
      </div>
      <div style={{ minWidth: 44, textAlign: "right", fontWeight: 700, color }}>{score.toFixed(0)}</div>
      <div
        style={{
          fontSize: 10,
          fontWeight: 700,
          color: modeColor,
          background: "#fff",
          border: `1px solid ${modeColor}`,
          padding: "2px 6px",
          borderRadius: 4,
          letterSpacing: 0.4,
        }}
      >
        {mode}
      </div>
    </div>
  );
}
