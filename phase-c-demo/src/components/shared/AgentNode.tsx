import Badge from "./Badge";

type Status = "RUNNING" | "VALIDATED" | "BLOCKED" | "WARNING";
type DataSourceLabel = "REAL" | "PRECOMPUTED" | "PROVIDED";

interface Props {
  name: string;
  status?: Status;
  input?: string;
  output?: string;
  confidence?: number;
  tool?: string;
  dataSource?: DataSourceLabel;
  gate?: boolean;
  gateNote?: string;
}

export default function AgentNode({ name, status, input, output, confidence, tool, dataSource, gate, gateNote }: Props) {
  if (gate) {
    return (
      <div
        style={{
          borderLeft: "4px solid var(--color-amber)",
          background: "#FFFBEB",
          padding: "10px 14px",
          borderRadius: 6,
          fontSize: 13,
          margin: "6px 0 6px 32px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontWeight: 700, color: "var(--color-amber)", fontSize: 11, letterSpacing: 0.5 }}>GATE</span>
          <span style={{ fontWeight: 600 }}>{name}</span>
        </div>
        {gateNote && <div style={{ marginTop: 4, color: "var(--color-text)", fontSize: 12 }}>{gateNote}</div>}
      </div>
    );
  }

  return (
    <div className="card" style={{ padding: 14 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 28, height: 28, borderRadius: 6,
              background: "var(--color-navy)", color: "#fff",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontWeight: 700, fontSize: 12,
            }}
          >
            {name.charAt(0)}
          </div>
          <div style={{ fontWeight: 600 }}>{name}</div>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          {status && <Badge status={status} />}
          {dataSource && <Badge status={dataSource} small />}
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, fontSize: 12 }}>
        <div>
          <div style={{ color: "var(--color-muted)", fontSize: 10, textTransform: "uppercase", letterSpacing: 0.4, fontWeight: 600 }}>Input</div>
          <div>{input}</div>
        </div>
        <div>
          <div style={{ color: "var(--color-muted)", fontSize: 10, textTransform: "uppercase", letterSpacing: 0.4, fontWeight: 600 }}>Output</div>
          <div>{output}</div>
        </div>
      </div>
      {(tool || confidence !== undefined) && (
        <div style={{ marginTop: 10, paddingTop: 8, borderTop: "1px solid var(--color-border)", display: "flex", gap: 16, fontSize: 11, color: "var(--color-muted)" }}>
          {tool && <div><span style={{ fontWeight: 600 }}>tool:</span> {tool}</div>}
          {confidence !== undefined && (
            <div>
              <span style={{ fontWeight: 600 }}>confidence:</span>{" "}
              <span style={{ color: confidence >= 0.7 ? "var(--color-green)" : confidence >= 0.5 ? "var(--color-amber)" : "var(--color-red)", fontWeight: 700 }}>
                {(confidence * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
