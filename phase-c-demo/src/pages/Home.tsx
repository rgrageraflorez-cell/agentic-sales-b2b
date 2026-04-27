import { Link } from "react-router-dom";
import Badge from "../components/shared/Badge";

const tnGrid = [
  { code: "TN10", title: "Razonamiento explícito (ReAct)",     desc: "Trace Reason → Act → Observe en cada paso del agente." },
  { code: "TN11", title: "Verificación de claims",             desc: "ClaimVerifier bloquea afirmaciones causales sin evidencia." },
  { code: "TN12", title: "Protocolo de silencio",              desc: "El sistema se detiene cuando la confianza < 0.50." },
  { code: "TN10", title: "Memoria persistente",                desc: "LearningEngine actualiza Wilson lower bounds entre campañas." },
  { code: "TN11", title: "Triangulación OSINT",                desc: "Mínimo 2 fuentes independientes antes de validar evidencia." },
  { code: "TN12", title: "Aprobación humana en el loop",        desc: "HumanReviewPanel exige firma analista antes de entrega." },
];

export default function Home() {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22 }}>ARIGRA · Phase C — Agentic Corporate Intelligence</h1>
        <p style={{ color: "var(--color-muted)", marginTop: 6, maxWidth: 760 }}>
          Demo visual del trabajo de la Fase C. Dos sistemas agénticos: el motor de captación B2B
          (operativo) y el agente de inteligencia competitiva (prototipo). Todos los datos llevan
          una etiqueta de origen visible.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: 16 }}>
        <div className="card" style={{ padding: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
            <h2 style={{ fontSize: 16 }}>B2B Lead Generation Agent</h2>
            <Badge status="VALIDATED">OPERATIONAL</Badge>
          </div>
          <div style={{ color: "var(--color-muted)", fontSize: 13, marginBottom: 14 }}>
            Pipeline de 4 fases (Recopilación · Inteligencia · Outreach · Aprendizaje) sobre el código real
            de ARIGRA. Captura empresas, las clusteriza por perfil, redacta emails personalizados, los humaniza
            y aprende de los resultados con cotas inferiores de Wilson.
          </div>
          <ul style={{ listStyle: "none", padding: 0, margin: "0 0 16px 0", fontSize: 13 }}>
            {[
              "Scraping + enrichment + validación de email",
              "Clustering KMeans con perfiles (incluye cluster -1 'unclassifiable')",
              "Humanizer agent (anti-IA-tells) con diff visible",
              "Loop de aprendizaje sobre 3 campañas reales",
            ].map((c) => (
              <li key={c} style={{ display: "flex", gap: 8, marginBottom: 6 }}>
                <span style={{ color: "var(--color-green)" }}>✓</span> {c}
              </li>
            ))}
          </ul>
          <Link
            to="/b2b"
            style={{
              display: "inline-block",
              background: "var(--color-blue)",
              color: "#fff",
              padding: "8px 16px",
              borderRadius: 6,
              textDecoration: "none",
              fontWeight: 600,
              fontSize: 13,
            }}
          >
            Run B2B Demo →
          </Link>
        </div>

        <div className="card" style={{ padding: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
            <h2 style={{ fontSize: 16 }}>Competitive Intelligence Agent</h2>
            <Badge status="WARNING">PROTOTYPE</Badge>
          </div>
          <div style={{ color: "var(--color-muted)", fontSize: 13, marginBottom: 14 }}>
            Demostración visual sobre el caso real de Club Foto Nauta (cliente actual de ARIGRA, ya en pipeline).
            Recibe un informe mensual y debe decidir si subir inversión publicitaria. Aplica ReAct, AMC,
            escenarios E1–E4, índice de confianza y protocolo de silencio.
          </div>
          <ul style={{ listStyle: "none", padding: 0, margin: "0 0 16px 0", fontSize: 13 }}>
            {[
              "Razonamiento ReAct paso a paso",
              "Triangulación OSINT con badges de fuente",
              "Matriz 2×2 de escenarios (dominante: E3)",
              "Protocolo de silencio si confianza < 0.50",
              "ClaimVerifier + revisión humana final",
            ].map((c) => (
              <li key={c} style={{ display: "flex", gap: 8, marginBottom: 6 }}>
                <span style={{ color: "var(--color-green)" }}>✓</span> {c}
              </li>
            ))}
          </ul>
          <Link
            to="/intelligence"
            style={{
              display: "inline-block",
              background: "var(--color-cyan)",
              color: "var(--color-navy)",
              padding: "8px 16px",
              borderRadius: 6,
              textDecoration: "none",
              fontWeight: 700,
              fontSize: 13,
            }}
          >
            Run Intelligence Demo →
          </Link>
        </div>
      </div>

      <div style={{ marginTop: 32 }}>
        <h2 style={{ fontSize: 15, marginBottom: 12 }}>Capacidades TN10–TN12 demostradas</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 12 }}>
          {tnGrid.map((cell, i) => (
            <div key={i} className="card" style={{ padding: 14 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 10, fontWeight: 700, color: "var(--color-blue)", letterSpacing: 0.5 }}>{cell.code}</span>
                <span style={{ color: "var(--color-green)" }}>✓</span>
              </div>
              <div style={{ fontWeight: 600, marginTop: 4 }}>{cell.title}</div>
              <div style={{ color: "var(--color-muted)", fontSize: 12, marginTop: 4 }}>{cell.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
