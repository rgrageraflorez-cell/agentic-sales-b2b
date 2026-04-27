import { useReducer } from "react";

type Status = "pending" | "approved" | "rejected" | "editing" | "more_evidence";

const FINDINGS = [
  { id: "f1", text: "Caída de ventas explicada por volumen, no por precio (98% del Δ)." },
  { id: "f2", text: "Hipótesis de fricción en checkout móvil (necesita validación)." },
  { id: "f3", text: "Recomendación E3: auditar funnel antes de subir inversión." },
  { id: "f4", text: "Plan de acción inmediato: pausar campañas con CPA > 30€." },
];

type State = Record<string, Status>;
type Action = { type: "set"; id: string; status: Status };

function reducer(s: State, a: Action): State {
  return { ...s, [a.id]: a.status };
}

const initial: State = Object.fromEntries(FINDINGS.map((f) => [f.id, "pending" as Status]));

const STATUS_COLOR: Record<Status, string> = {
  pending: "#94a3b8",
  approved: "var(--color-green)",
  rejected: "var(--color-red)",
  editing: "var(--color-blue)",
  more_evidence: "var(--color-amber)",
};

export default function HumanReviewPanel() {
  const [state, dispatch] = useReducer(reducer, initial);
  const allApproved = FINDINGS.every((f) => state[f.id] === "approved");

  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 10 }}>
        <h3 style={{ fontSize: 14 }}>Human Review · firma analista</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: precomputed_demo</div>
      </div>

      {FINDINGS.map((f) => {
        const st = state[f.id];
        return (
          <div key={f.id} style={{ padding: "12px 0", borderTop: "1px solid var(--color-border)" }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
              <span style={{ width: 10, height: 10, borderRadius: "50%", background: STATUS_COLOR[st], marginTop: 5, flexShrink: 0 }} />
              <div style={{ flex: 1, fontSize: 13 }}>{f.text}</div>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 0.4, color: STATUS_COLOR[st], textTransform: "uppercase", minWidth: 90, textAlign: "right" }}>
                {st === "more_evidence" ? "MORE EVIDENCE" : st}
              </div>
            </div>
            <div style={{ marginTop: 8, marginLeft: 20, display: "flex", gap: 6, flexWrap: "wrap" }}>
              <Btn label="Approve"           color="var(--color-green)" onClick={() => dispatch({ type: "set", id: f.id, status: "approved" })} />
              <Btn label="Edit wording"      color="var(--color-blue)"  onClick={() => dispatch({ type: "set", id: f.id, status: "editing" })} />
              <Btn label="Request evidence"  color="var(--color-amber)" onClick={() => dispatch({ type: "set", id: f.id, status: "more_evidence" })} />
              <Btn label="Reject"            color="var(--color-red)"   onClick={() => dispatch({ type: "set", id: f.id, status: "rejected" })} />
            </div>
          </div>
        );
      })}

      <div style={{ marginTop: 14, padding: 10, background: "#F8FAFC", borderRadius: 6, fontSize: 12, color: "var(--color-muted)", borderTop: "1px solid var(--color-border)" }}>
        Human analyst approval required before client delivery.
      </div>

      {allApproved && (
        <div style={{ marginTop: 10, padding: 12, background: "#DCFCE7", border: "1px solid #16A34A", borderRadius: 6, color: "#15803D", fontWeight: 600 }}>
          ✓ Analysis approved for client delivery.
        </div>
      )}
    </div>
  );
}

function Btn({ label, color, onClick }: { label: string; color: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: "#fff",
        color,
        border: `1px solid ${color}`,
        padding: "4px 10px",
        borderRadius: 4,
        fontSize: 11,
        fontWeight: 600,
        cursor: "pointer",
      }}
    >
      {label}
    </button>
  );
}
