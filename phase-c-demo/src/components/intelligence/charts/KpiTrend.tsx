import { CartesianGrid, Legend, Line, LineChart, ReferenceArea, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { kpiHistory } from "../../../data/extendedData";

export default function KpiTrend() {
  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <h3 style={{ fontSize: 14 }}>Evolución 12 meses · ventas, conversión y CPA</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: provided_report (extrapolado)</div>
      </div>
      <div style={{ width: "100%", height: 260 }}>
        <ResponsiveContainer>
          <LineChart data={kpiHistory} margin={{ top: 6, right: 16, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="month" fontSize={11} />
            <YAxis yAxisId="left" fontSize={11} />
            <YAxis yAxisId="right" orientation="right" fontSize={11} />
            <Tooltip contentStyle={{ fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <ReferenceArea yAxisId="left" x1="Ene 26" x2="Feb 26" fill="#FEF2F2" stroke="#FECACA" label={{ value: "Crisis", fontSize: 10, fill: "#DC2626" }} />
            <Line yAxisId="left"  type="monotone" dataKey="ventas"     stroke="#0E7CFF" strokeWidth={2} dot name="Ventas brutas (€)" />
            <Line yAxisId="right" type="monotone" dataKey="conversion" stroke="#16A34A" strokeWidth={2} dot name="Conversión (%)" />
            <Line yAxisId="right" type="monotone" dataKey="cpa"        stroke="#DC2626" strokeWidth={2} dot strokeDasharray="4 2" name="CPA (€)" />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 6 }}>
        Caída brusca en ene-feb 2026: ventas pierden ~50% del pico de diciembre, CPA se dispara, conversión rompe el suelo histórico de 1.5%.
      </div>
    </div>
  );
}
