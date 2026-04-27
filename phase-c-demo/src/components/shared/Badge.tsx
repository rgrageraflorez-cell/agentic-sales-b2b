type Status =
  | "RUNNING" | "VALIDATED" | "BLOCKED" | "WARNING" | "APPROVED"
  | "LIMITED" | "PRECOMPUTED" | "REAL" | "PROVIDED"
  | "FULL" | "SILENCE" | "DOMINANT"
  | "HIGH" | "MEDIUM" | "LOW"
  | "PREOCUPANTE" | "ESTABLE" | "POSITIVO"
  | "LIMITADA" | "INSUFICIENTE"
  | "UNCLASSIFIABLE";

interface Props {
  status: Status;
  children?: React.ReactNode;
  small?: boolean;
}

const COLORS: Record<Status, { bg: string; fg: string; border?: string }> = {
  RUNNING:        { bg: "#DBEAFE", fg: "#0E7CFF" },
  VALIDATED:      { bg: "#DCFCE7", fg: "#15803D" },
  BLOCKED:        { bg: "#FEE2E2", fg: "#B91C1C" },
  WARNING:        { bg: "#FEF3C7", fg: "#B45309" },
  APPROVED:       { bg: "#DCFCE7", fg: "#15803D" },
  LIMITED:        { bg: "#FEF3C7", fg: "#B45309" },
  PRECOMPUTED:    { bg: "#E5E7EB", fg: "#374151" },
  REAL:           { bg: "#CFFAFE", fg: "#0E7490" },
  PROVIDED:       { bg: "#E0E7FF", fg: "#4338CA" },
  FULL:           { bg: "#DCFCE7", fg: "#15803D" },
  SILENCE:        { bg: "#FEE2E2", fg: "#B91C1C" },
  DOMINANT:       { bg: "#FEF3C7", fg: "#B45309" },
  HIGH:           { bg: "#FEE2E2", fg: "#B91C1C" },
  MEDIUM:         { bg: "#FEF3C7", fg: "#B45309" },
  LOW:            { bg: "#E5E7EB", fg: "#374151" },
  PREOCUPANTE:    { bg: "#FEE2E2", fg: "#B91C1C" },
  ESTABLE:        { bg: "#E0E7FF", fg: "#4338CA" },
  POSITIVO:       { bg: "#DCFCE7", fg: "#15803D" },
  LIMITADA:       { bg: "#FEF3C7", fg: "#B45309" },
  INSUFICIENTE:   { bg: "#FEE2E2", fg: "#B91C1C" },
  UNCLASSIFIABLE: { bg: "#E5E7EB", fg: "#374151" },
};

export default function Badge({ status, children, small }: Props) {
  const c = COLORS[status];
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        background: c.bg,
        color: c.fg,
        padding: small ? "2px 6px" : "3px 8px",
        borderRadius: 999,
        fontSize: small ? 10 : 11,
        fontWeight: 600,
        letterSpacing: 0.3,
        textTransform: "uppercase",
        lineHeight: 1.4,
        whiteSpace: "nowrap",
      }}
    >
      {status === "RUNNING" && <span className="spinner" style={{ width: 8, height: 8, borderWidth: 1.5 }} />}
      {children ?? status}
    </span>
  );
}
