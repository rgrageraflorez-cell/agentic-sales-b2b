import Badge from "../shared/Badge";

interface Props { title: string; }

export default function Header({ title }: Props) {
  return (
    <header
      style={{
        position: "fixed",
        top: 0,
        left: 220,
        right: 0,
        height: 56,
        background: "#fff",
        borderBottom: "1px solid var(--color-border)",
        display: "flex",
        alignItems: "center",
        padding: "0 24px",
        zIndex: 10,
      }}
    >
      <div style={{ fontWeight: 600, fontSize: 15 }}>{title}</div>
      <div style={{ marginLeft: "auto" }}>
        <Badge status="WARNING">DEMO MODE</Badge>
      </div>
    </header>
  );
}
