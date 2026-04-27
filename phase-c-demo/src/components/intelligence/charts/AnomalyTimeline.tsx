import { Area, AreaChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Scatter, ComposedChart, Tooltip, XAxis, YAxis } from "recharts";
import { anomalyTimeline } from "../../../data/extendedData";

export default function AnomalyTimeline() {
  const anomalies = anomalyTimeline.filter((p) => p.isAnomaly);
  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <h3 style={{ fontSize: 14 }}>Detección de anomalías · carrito abandonado (febrero)</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: provided_report</div>
      </div>
      <div style={{ width: "100%", height: 200 }}>
        <ResponsiveContainer>
          <ComposedChart data={anomalyTimeline} margin={{ top: 6, right: 16, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="ab" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#0E7CFF" stopOpacity={0.4} />
                <stop offset="100%" stopColor="#0E7CFF" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="date" fontSize={11} />
            <YAxis fontSize={11} unit="%" domain={[40, 80]} />
            <Tooltip contentStyle={{ fontSize: 12 }} />
            <ReferenceLine y={62} stroke="#16A34A" strokeDasharray="3 3" label={{ value: "Histórico (62%)", fontSize: 10, fill: "#16A34A", position: "left" }} />
            <ReferenceLine y={65} stroke="#F59E0B" strokeDasharray="3 3" label={{ value: "Umbral auditoría (65%)", fontSize: 10, fill: "#F59E0B" }} />
            <Area type="monotone" dataKey="value" stroke="#0E7CFF" strokeWidth={2} fill="url(#ab)" />
            <Scatter data={anomalies} dataKey="value" fill="#DC2626" shape="circle" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 6 }}>
        6 puntos consecutivos por encima del umbral sectorial (65%). El cambio se inicia el 13 de febrero y se mantiene → patrón sistémico, no ruido.
      </div>
    </div>
  );
}
