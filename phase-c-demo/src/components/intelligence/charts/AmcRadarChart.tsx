import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { amcRadar } from "../../../data/extendedData";

const COLORS = ["#0E7CFF", "#16A34A", "#DC2626"];

export default function AmcRadarChart() {
  // Reshape: dimensions on X axis, value per competitor.
  const dimensions = ["awareness", "motivation", "capability"] as const;
  const data = dimensions.map((dim) => {
    const row: { dimension: string; [k: string]: string | number } = { dimension: dim.charAt(0).toUpperCase() + dim.slice(1) };
    amcRadar.forEach((c) => {
      row[c.competitor] = c[dim];
    });
    return row;
  });

  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <h3 style={{ fontSize: 14 }}>AMC · radar de amenaza competitiva</h3>
        <div style={{ fontSize: 10, color: "var(--color-muted)", fontStyle: "italic" }}>source: precomputed_demo</div>
      </div>
      <div style={{ width: "100%", height: 280 }}>
        <ResponsiveContainer>
          <RadarChart data={data}>
            <PolarGrid stroke="#E2E8F0" />
            <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 11 }} />
            <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 9 }} />
            {amcRadar.map((c, i) => (
              <Radar key={c.competitor} name={c.competitor} dataKey={c.competitor} stroke={COLORS[i]} fill={COLORS[i]} fillOpacity={0.18} />
            ))}
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ fontSize: 12 }} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 4 }}>
        Amazon domina capability/motivation pero su awareness sobre Nauta es baja (es un riesgo estructural, no dirigido). Foto Sport es el rival activo más alineado.
      </div>
    </div>
  );
}
