import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell } from "recharts";
import {
  contentVolumeRecommendation,
  tiktokScripts,
  instagramPosts,
  emailNewsletter,
  contentCalendar,
} from "../../../data/extendedData";
import Badge from "../../shared/Badge";
import { cognitiveOutput } from "../../../data/intelligenceDemoData";
import TikTokScriptCard from "./TikTokScriptCard";
import InstagramPostCard from "./InstagramPostCard";

const CHANNEL_COLOR: Record<string, string> = {
  TikTok: "#0F172A",
  Instagram: "#E1306C",
  Email: "#0E7CFF",
  Blog: "#16A34A",
};

export default function ContentBrief() {
  const [tab, setTab] = useState<"calendar" | "tiktok" | "instagram" | "email" | "volume">("calendar");

  return (
    <div>
      <CognitiveBanner />

      <div className="card" style={{ padding: 0, overflow: "hidden", marginTop: 14 }}>
        <div style={{ display: "flex", borderBottom: "1px solid var(--color-border)" }}>
          {(
            [
              { k: "calendar", label: "📅 Calendario semanal" },
              { k: "tiktok",   label: "🎬 TikTok · 7 guiones" },
              { k: "instagram", label: "📸 Instagram · 5 posts" },
              { k: "email",    label: "📧 Newsletter" },
              { k: "volume",   label: "📊 Volumen recomendado" },
            ] as const
          ).map((t) => (
            <button
              key={t.k}
              onClick={() => setTab(t.k)}
              style={{
                flex: 1,
                padding: "10px 12px",
                background: tab === t.k ? "#fff" : "#F8FAFC",
                border: 0,
                borderBottom: tab === t.k ? "2px solid var(--color-blue)" : "2px solid transparent",
                fontSize: 12,
                fontWeight: tab === t.k ? 700 : 500,
                color: tab === t.k ? "var(--color-text)" : "var(--color-muted)",
                cursor: "pointer",
              }}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div style={{ padding: 16 }}>
          {tab === "calendar" && <Calendar />}
          {tab === "tiktok" && <TikTokGrid />}
          {tab === "instagram" && <InstagramGrid />}
          {tab === "email" && <EmailPreview />}
          {tab === "volume" && <VolumeChart />}
        </div>
      </div>
    </div>
  );
}

function CognitiveBanner() {
  const c = cognitiveOutput;
  return (
    <div
      style={{
        background: "linear-gradient(135deg, #0B1F3A 0%, #1e3a8a 100%)",
        color: "#fff",
        padding: 18,
        borderRadius: 8,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: "#20C7D9", letterSpacing: 0.5, textTransform: "uppercase" }}>
          Output cognitivo · brief generativo
        </span>
        <Badge status={c.status} small />
        <Badge status="LIMITADA" small />
      </div>
      <div style={{ fontSize: 14, marginTop: 8, lineHeight: 1.6, maxWidth: 820 }}>
        {c.summary}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 14 }}>
        <div style={{ padding: 10, background: "rgba(22,163,74,0.18)", borderRadius: 6, borderLeft: "3px solid #16A34A" }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: "#86EFAC", textTransform: "uppercase", letterSpacing: 0.4 }}>
            Hallazgo clave
          </div>
          <div style={{ fontSize: 12, marginTop: 4 }}>{c.keyFinding}</div>
        </div>
        <div style={{ padding: 10, background: "rgba(245,158,11,0.18)", borderRadius: 6, borderLeft: "3px solid #F59E0B" }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: "#FCD34D", textTransform: "uppercase", letterSpacing: 0.4 }}>
            Incertidumbre principal
          </div>
          <div style={{ fontSize: 12, marginTop: 4 }}>{c.mainUncertainty}</div>
        </div>
      </div>
      <div style={{ marginTop: 14, paddingTop: 12, borderTop: "1px solid rgba(255,255,255,0.15)", fontSize: 13 }}>
        <strong style={{ color: "#20C7D9" }}>Recomendación accionable de contenido:</strong> mientras se audita el
        checkout, mover volumen al canal social orgánico. Plan de 7 días con TikTok diario, 5 IG, 1 newsletter
        y 1 post de blog. Cada pieza está atada a un dato concreto del informe de febrero.
      </div>
    </div>
  );
}

function Calendar() {
  return (
    <div>
      <div style={{ fontSize: 12, color: "var(--color-muted)", marginBottom: 12 }}>
        Ventana de 7 días · 7 TikToks (1/día) · 5 Instagram · 1 newsletter · 1 post SEO. Total: <strong>14 piezas/semana</strong> vs <strong>5,5 actuales</strong>.
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 8 }}>
        {contentCalendar.map((day) => (
          <div key={day.day} className="card" style={{ padding: 10, minHeight: 220 }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: 6, borderBottom: "1px solid var(--color-border)", paddingBottom: 6, marginBottom: 8 }}>
              <span style={{ fontWeight: 700, fontSize: 13 }}>{day.day}</span>
              <span style={{ fontSize: 11, color: "var(--color-muted)" }}>{day.date}</span>
            </div>
            {day.channels.map((c, i) => (
              <div
                key={i}
                style={{
                  borderLeft: `3px solid ${CHANNEL_COLOR[c.channel]}`,
                  background: "#F8FAFC",
                  padding: "6px 8px",
                  marginBottom: 6,
                  borderRadius: 4,
                }}
              >
                <div style={{ fontSize: 10, fontWeight: 700, color: CHANNEL_COLOR[c.channel], textTransform: "uppercase", letterSpacing: 0.5 }}>
                  {c.channel}
                </div>
                <div style={{ fontSize: 11, marginTop: 2 }}>{c.title}</div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

function TikTokGrid() {
  return (
    <div>
      <div style={{ fontSize: 12, color: "var(--color-muted)", marginBottom: 12 }}>
        Frecuencia recomendada: <strong>1 TikTok al día</strong>. Cada guion incluye hook, beats, CTA, hashtags,
        música sugerida y por qué <em>específicamente</em> este vídeo para Club Foto Nauta.
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: 12 }}>
        {tiktokScripts.map((s) => (
          <TikTokScriptCard key={s.id} script={s} />
        ))}
      </div>
    </div>
  );
}

function InstagramGrid() {
  return (
    <div>
      <div style={{ fontSize: 12, color: "var(--color-muted)", marginBottom: 12 }}>
        5 piezas semanales. Mezcla de carrusel educativo (mayor guardado) + Reels (mayor alcance) + Story interactiva.
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: 12 }}>
        {instagramPosts.map((p) => (
          <InstagramPostCard key={p.id} post={p} />
        ))}
      </div>
    </div>
  );
}

function EmailPreview() {
  const e = emailNewsletter;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: 16 }}>
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ background: "#F8FAFC", padding: "10px 14px", borderBottom: "1px solid var(--color-border)" }}>
          <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 600 }}>Asunto</div>
          <div style={{ fontWeight: 600, fontSize: 14 }}>{e.subject}</div>
          <div style={{ fontSize: 11, color: "var(--color-muted)", marginTop: 4 }}>preheader: {e.preheader}</div>
        </div>
        <div style={{ padding: 16, fontSize: 13, lineHeight: 1.7, whiteSpace: "pre-wrap" }}>{e.body}</div>
      </div>
      <div className="card" style={{ padding: 14, height: "fit-content" }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: "var(--color-muted)", textTransform: "uppercase", letterSpacing: 0.5 }}>Audiencia</div>
        <div style={{ fontSize: 12, marginTop: 4, marginBottom: 10 }}>{e.audience}</div>
        <div style={{ fontSize: 11, fontWeight: 700, color: "var(--color-muted)", textTransform: "uppercase", letterSpacing: 0.5 }}>Por qué este email</div>
        <div style={{ fontSize: 12, marginTop: 4 }}>{e.rationale}</div>
      </div>
    </div>
  );
}

function VolumeChart() {
  return (
    <div>
      <div style={{ fontSize: 12, color: "var(--color-muted)", marginBottom: 12 }}>
        Volumen de publicación actual vs recomendado. Cada barra responde a un dato concreto del informe.
      </div>
      <div style={{ width: "100%", height: 240 }}>
        <ResponsiveContainer>
          <BarChart data={contentVolumeRecommendation} margin={{ top: 6, right: 16, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="channel" fontSize={11} />
            <YAxis fontSize={11} />
            <Tooltip contentStyle={{ fontSize: 12 }} formatter={(v: number) => [`${v}/sem`, ""]} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Bar dataKey="current_per_week"     name="Actual"      fill="#94a3b8" />
            <Bar dataKey="recommended_per_week" name="Recomendado" fill="#0E7CFF">
              {contentVolumeRecommendation.map((_, i) => <Cell key={i} fill="#0E7CFF" />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div style={{ marginTop: 10 }}>
        {contentVolumeRecommendation.map((r) => (
          <div key={r.channel} style={{ padding: 10, borderTop: "1px solid var(--color-border)", fontSize: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
              <span style={{ fontWeight: 600, color: CHANNEL_COLOR[r.channel] || "var(--color-text)" }}>{r.channel}</span>
              <Badge status="WARNING" small>{r.current_per_week}/sem → {r.recommended_per_week}/sem</Badge>
            </div>
            <div style={{ color: "var(--color-text)" }}>{r.rationale}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
