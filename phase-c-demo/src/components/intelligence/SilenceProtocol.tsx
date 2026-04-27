interface Props { onResume: () => void; }

const ACTIONS = [
  "Re-ejecutar la recolección OSINT con un mínimo de 3 fuentes independientes por afirmación.",
  "Solicitar al cliente datos faltantes de margen bruto y atribución por canal.",
  "Auditar pipeline de KPIs para descartar errores de medición (GA4 + Stripe).",
  "Validar manualmente las dos reseñas que disparan la hipótesis de checkout móvil.",
  "Diferir cualquier recomendación accionable hasta el próximo ciclo de revisión.",
];

export default function SilenceProtocol({ onResume }: Props) {
  return (
    <div className="card" style={{ padding: 20, borderTop: "4px solid var(--color-red)", background: "#FEF2F2" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
        <span style={{ fontSize: 22 }}>🛑</span>
        <h2 style={{ fontSize: 18, color: "var(--color-red)" }}>SILENCE PROTOCOL ACTIVATED</h2>
      </div>
      <div style={{ color: "#7F1D1D", fontSize: 13, marginBottom: 14 }}>
        Confidence index below minimum threshold (0.50). El agente <strong>se rehúsa a emitir conclusiones</strong> hasta
        completar las acciones de auditoría siguientes.
      </div>
      <ol style={{ paddingLeft: 22, fontSize: 13, color: "var(--color-text)" }}>
        {ACTIONS.map((a, i) => (
          <li key={i} style={{ marginBottom: 6 }}>{a}</li>
        ))}
      </ol>
      <button
        onClick={onResume}
        style={{
          marginTop: 10,
          background: "var(--color-navy)",
          color: "#fff",
          border: 0,
          padding: "8px 16px",
          borderRadius: 6,
          fontWeight: 600,
          fontSize: 13,
          cursor: "pointer",
        }}
      >
        Resume normal analysis
      </button>
    </div>
  );
}
