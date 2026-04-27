import { NavLink } from "react-router-dom";

const items = [
  { to: "/", label: "Home" },
  { to: "/b2b", label: "B2B System" },
  { to: "/intelligence", label: "Intelligence System" },
];

export default function Sidebar() {
  return (
    <aside
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        bottom: 0,
        width: 220,
        background: "var(--color-navy)",
        color: "#fff",
        display: "flex",
        flexDirection: "column",
        zIndex: 20,
      }}
    >
      <div style={{ padding: "20px 18px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        <div style={{ fontWeight: 700, fontSize: 18, letterSpacing: 1.5 }}>ARIGRA</div>
        <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2, letterSpacing: 0.5 }}>AGENTIC SYSTEMS</div>
      </div>
      <nav style={{ padding: 8, flex: 1 }}>
        {items.map((it) => (
          <NavLink
            key={it.to}
            to={it.to}
            end={it.to === "/"}
            style={({ isActive }) => ({
              display: "block",
              padding: "10px 14px",
              margin: "2px 0",
              borderRadius: 6,
              borderLeft: isActive ? "3px solid var(--color-cyan)" : "3px solid transparent",
              background: isActive ? "rgba(32,199,217,0.12)" : "transparent",
              color: "#fff",
              textDecoration: "none",
              fontSize: 13,
              fontWeight: isActive ? 600 : 400,
              transition: "background 150ms",
            })}
          >
            {it.label}
          </NavLink>
        ))}
      </nav>
      <div style={{ padding: 14, fontSize: 10, color: "#64748B", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
        Phase C Demo · v0.1
      </div>
    </aside>
  );
}
