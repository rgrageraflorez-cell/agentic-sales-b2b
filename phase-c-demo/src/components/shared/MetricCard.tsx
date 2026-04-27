interface Props {
  label: string;
  value: string | number;
  delta?: string;
  direction?: "up" | "down" | "flat";
  notes?: string;
  dataSource?: string;
}

export default function MetricCard({ label, value, delta, direction, notes, dataSource }: Props) {
  const color = direction === "up" ? "var(--color-green)" : direction === "down" ? "var(--color-red)" : "var(--color-muted)";
  return (
    <div className="card" style={{ padding: 14 }}>
      <div style={{ fontSize: 11, color: "var(--color-muted)", textTransform: "uppercase", letterSpacing: 0.4, fontWeight: 600 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 700, marginTop: 4 }}>{value}</div>
      {delta && (
        <div style={{ fontSize: 12, color, fontWeight: 600, marginTop: 2 }}>
          {direction === "up" ? "▲" : direction === "down" ? "▼" : "■"} {delta}
        </div>
      )}
      {notes && <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 4 }}>{notes}</div>}
      {dataSource && <div style={{ fontSize: 10, color: "var(--color-muted)", marginTop: 6, fontStyle: "italic" }}>source: {dataSource}</div>}
    </div>
  );
}
