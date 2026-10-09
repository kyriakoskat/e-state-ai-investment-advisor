import { Link, useParams } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle, ArrowLeft, Droplet, Leaf, Mountain, Send, Sun,
} from "lucide-react";

import AppHeader from "../components/AppHeader";
import Chatbot from "../components/Chatbot";
import PlotMap from "../components/PlotMap";
import { getProperty } from "../api";
import { SCORE_LABEL, type InvestmentScores, type Property } from "../types";
import { useSession } from "../store";

export function PlotPage() {
  const { plotId } = useParams({ strict: false }) as { plotId: string };
  const { data: plot } = useQuery<Property>({
    queryKey: ["property", plotId], queryFn: () => getProperty(plotId), enabled: !!plotId,
  });
  const { dispatch } = useSession();

  if (!plot) {
    return (
      <div className="min-h-screen flex flex-col">
        <AppHeader />
        <div className="flex-1 grid place-items-center text-muted-foreground">Loading plot…</div>
      </div>
    );
  }

  const scores = Object.entries(plot.investment_scores) as [keyof InvestmentScores, number][];
  scores.sort((a, b) => b[1] - a[1]);
  const top = scores[0];

  const ask = (text: string) => {
    dispatch({ type: "user_message", content: text });
    // The chat input + streaming is driven from the floating Chatbot; we just
    // pre-fill the visible chat with the question to nudge the user to send it.
  };

  return (
    <div className="min-h-screen flex flex-col">
      <AppHeader />

      <div className="border-b border-border px-6 py-2 bg-card/40">
        <Link to="/" className="text-[11px] text-muted-foreground hover:text-primary tracking-widest uppercase flex items-center gap-1.5 font-mono">
          <ArrowLeft className="w-3 h-3" /> Back to dashboard
        </Link>
      </div>

      <section className="px-6 py-6 border-b border-border">
        <div className="max-w-7xl mx-auto grid md:grid-cols-[1fr_auto] gap-6 items-end">
          <div>
            <div className="terminal-label mb-1">PLOT · {plot.property_id}</div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight">{plot.plot_name}</h1>
            <div className="text-sm text-muted-foreground mt-1 font-mono">
              {plot.region} · {plot.location.latitude.toFixed(4)}, {plot.location.longitude.toFixed(4)}
            </div>
            <p className="text-sm mt-3 max-w-2xl leading-relaxed">
              {plot.agent_ready_summary?.one_liner ?? `${plot.plot_name}: ${plot.recommended_use.final_recommendation}.`}
            </p>
          </div>
          <div className="grid grid-cols-3 gap-3 text-right">
            <Metric label="Area" value={`${(plot.area_m2 / 1000).toFixed(0)}k m²`} />
            <Metric label="Asking" value={`€${(plot.price_eur / 1e6).toFixed(2)}M`} />
            <Metric label="Top score" value={`${top[1].toFixed(0)}/100`} accent />
          </div>
        </div>
      </section>

      <div className="grid lg:grid-cols-[1fr_360px] gap-px bg-border">
        <main className="bg-background p-6 space-y-6">
          <Panel title="Investment Score Matrix" subtitle="Precomputed deterministic scores">
            <div className="space-y-3">
              {scores.map(([key, value]) => (
                <div key={key} className="border border-border p-4 rounded-sm">
                  <div className="flex items-start justify-between mb-2 gap-4">
                    <div>
                      <div className="text-sm font-bold tracking-wide">{SCORE_LABEL[key]}</div>
                      <div className="text-[10px] text-muted-foreground tracking-widest uppercase font-mono mt-0.5">
                        column: {key}
                      </div>
                    </div>
                    <ScoreBadge score={value} />
                  </div>
                  <div className="w-full h-1 bg-muted overflow-hidden rounded-sm">
                    <div
                      className="h-full"
                      style={{
                        width: `${value}%`,
                        background: value >= 75 ? "var(--color-positive)" : value >= 50 ? "var(--color-warning)" : "var(--color-negative)",
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Spectral Indices" subtitle="Hyperspectral-derived signals">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {plot.spectral_indices.NDVI && (
                <IdxCard icon={<Leaf className="w-3.5 h-3.5" />} label="NDVI" value={plot.spectral_indices.NDVI.mean.toFixed(3)} hint="vegetation"
                  tone={plot.spectral_indices.NDVI.mean > 0.6 ? "positive" : plot.spectral_indices.NDVI.mean > 0.4 ? "warning" : "negative"} />
              )}
              {plot.spectral_indices.NDWI && (
                <IdxCard icon={<Droplet className="w-3.5 h-3.5" />} label="NDWI" value={plot.spectral_indices.NDWI.mean.toFixed(3)} hint="water content" tone="info" />
              )}
              {plot.spectral_indices.NDMI && (
                <IdxCard icon={<Droplet className="w-3.5 h-3.5" />} label="NDMI" value={plot.spectral_indices.NDMI.mean.toFixed(3)} hint="moisture" tone="info" />
              )}
              {plot.spectral_indices.NDRE && (
                <IdxCard icon={<Leaf className="w-3.5 h-3.5" />} label="NDRE" value={plot.spectral_indices.NDRE.mean.toFixed(3)} hint="red-edge" tone="info" />
              )}
              {plot.spectral_indices.NBR && (
                <IdxCard icon={<Sun className="w-3.5 h-3.5" />} label="NBR" value={plot.spectral_indices.NBR.mean.toFixed(3)} hint="burn ratio" tone="info" />
              )}
              {plot.spectral_indices.GNDVI && (
                <IdxCard icon={<Leaf className="w-3.5 h-3.5" />} label="GNDVI" value={plot.spectral_indices.GNDVI.mean.toFixed(3)} hint="green-NDVI" tone="info" />
              )}
            </div>
          </Panel>

          <Panel title="Terrain" subtitle="Constraint analysis">
            <div className="grid grid-cols-3 gap-3">
              <IdxCard icon={<Mountain className="w-3.5 h-3.5" />} label="Slope" value={`${plot.terrain_analysis.slope_degrees}°`} hint="degrees"
                tone={(plot.terrain_analysis.slope_degrees ?? 0) > 12 ? "negative" : (plot.terrain_analysis.slope_degrees ?? 0) > 6 ? "warning" : "positive"} />
              <IdxCard icon={<Mountain className="w-3.5 h-3.5" />} label="Suitability" value={(plot.terrain_analysis.terrain_suitability_score ?? 0).toFixed(1)} hint="score"
                tone={(plot.terrain_analysis.terrain_suitability_score ?? 0) > 35 ? "positive" : "warning"} />
              <IdxCard icon={<AlertTriangle className="w-3.5 h-3.5" />} label="Limitation" value={(plot.terrain_analysis.terrain_limitation_label ?? "—").replace(/_/g, " ")} hint="label"
                tone={plot.terrain_analysis.terrain_limitation_label?.includes("severe") ? "negative" :
                      plot.terrain_analysis.terrain_limitation_label?.includes("high") ? "warning" : "positive"} />
            </div>
          </Panel>

          {plot.risk_flags?.length > 0 && (
            <Panel title="Risk flags" subtitle="From the ML pipeline">
              <div className="flex flex-wrap gap-2">
                {plot.risk_flags.map((r) => (
                  <span key={r} className="text-[11px] tracking-wider uppercase font-mono border border-warning text-warning px-2 py-1 rounded-sm">
                    {r.replace(/_/g, " ")}
                  </span>
                ))}
              </div>
            </Panel>
          )}

          {plot.suggested_crops?.length > 0 && (
            <Panel title="Suggested crops" subtitle="If agriculture is in play">
              <div className="flex flex-wrap gap-2">
                {plot.suggested_crops.map((c) => (
                  <span key={c} className="text-xs border border-border px-2 py-1 rounded-sm bg-card">
                    {c}
                  </span>
                ))}
              </div>
            </Panel>
          )}
        </main>

        <aside className="bg-background p-4 space-y-4">
          <div>
            <div className="terminal-label mb-2">// Geo Locator</div>
            <div className="h-64 border border-border rounded-sm overflow-hidden">
              <PlotMap activeId={plot.property_id} />
            </div>
          </div>

          <div className="terminal-panel p-4 border-primary rounded-sm">
            <div className="terminal-label text-primary mb-2">// ML Verdict</div>
            <div className="text-sm font-bold mb-1">
              {plot.recommended_use.final_recommendation?.replace(/_/g, " ") ?? "—"}
            </div>
            <div className="text-xs text-muted-foreground">
              Confidence: <span className="terminal-value font-bold">{plot.recommended_use.confidence ?? "—"}</span>
            </div>
            <div className="text-xs text-muted-foreground mt-2 leading-relaxed">
              {plot.agent_ready_summary?.one_liner}
            </div>
          </div>

          <div className="terminal-panel p-4 rounded-sm">
            <div className="terminal-label mb-2">Ask the Copilot</div>
            <button
              onClick={() => ask(`Tell me more about ${plot.plot_name} — pros, cons, who should pick it.`)}
              className="w-full text-left text-xs px-3 py-2 border border-border hover:border-primary hover:bg-card rounded-sm flex items-center justify-between"
            >
              <span>Why this plot?</span><Send className="w-3 h-3" />
            </button>
            <button
              onClick={() => ask(`What are the main risks of investing in ${plot.plot_name}?`)}
              className="w-full text-left text-xs px-3 py-2 border border-border hover:border-primary hover:bg-card rounded-sm flex items-center justify-between mt-2"
            >
              <span>What are the risks?</span><Send className="w-3 h-3" />
            </button>
          </div>
        </aside>
      </div>

      <Chatbot />
    </div>
  );
}

function Metric({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div>
      <div className="terminal-label">{label}</div>
      <div className={"text-xl font-bold terminal-value " + (accent ? "text-primary ticker-glow" : "")}>{value}</div>
    </div>
  );
}

function ScoreBadge({ score }: { score: number }) {
  const tone = score >= 75 ? "text-positive border-positive"
             : score >= 50 ? "text-warning border-warning"
             : "text-negative border-negative";
  return (
    <div className={"border px-2 py-1 text-lg font-bold terminal-value min-w-[52px] text-center rounded-sm " + tone}>
      {score.toFixed(0)}
    </div>
  );
}

function IdxCard({ icon, label, value, hint, tone }: {
  icon: React.ReactNode; label: string; value: string; hint: string;
  tone: "positive" | "warning" | "negative" | "info";
}) {
  const cls = { positive: "text-positive", warning: "text-warning", negative: "text-negative", info: "text-info" }[tone];
  return (
    <div className="border border-border p-3 rounded-sm">
      <div className="flex items-center gap-1.5 terminal-label">{icon} {label}</div>
      <div className={"text-lg font-bold terminal-value mt-1 " + cls}>{value}</div>
      <div className="text-[10px] text-muted-foreground">{hint}</div>
    </div>
  );
}

function Panel({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <section>
      <div className="flex items-baseline justify-between mb-3 pb-2 border-b border-border">
        <h2 className="text-sm font-bold tracking-widest uppercase font-mono">{title}</h2>
        {subtitle && <span className="text-[10px] text-muted-foreground tracking-wider uppercase font-mono">{subtitle}</span>}
      </div>
      {children}
    </section>
  );
}
