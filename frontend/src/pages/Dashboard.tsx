import { Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, TrendingUp } from "lucide-react";

import AppHeader from "../components/AppHeader";
import Chatbot from "../components/Chatbot";
import PlotMap from "../components/PlotMap";
import { AgentTabs } from "../components/AgentTabs";
import { listProperties } from "../api";
import { bestScore, type Property } from "../types";
import { useSession } from "../store";

export function Dashboard() {
  const { data: plots = [] } = useQuery<Property[]>({
    queryKey: ["properties"], queryFn: listProperties,
  });
  const { profile, candidates } = useSession();
  const highlightIds = candidates.map((c) => c.property_id);

  return (
    <div className="min-h-screen flex flex-col">
      <AppHeader />

      <Ticker plots={plots} />

      <section className="px-6 py-8 border-b border-border">
        <div className="max-w-7xl mx-auto">
          <div className="terminal-label mb-2">// Mission Brief</div>
          <h1 className="text-3xl md:text-5xl font-bold tracking-tight">
            Multi-agent land investment advisor.
            <span className="text-primary ticker-glow"> One conversation. One recommendation.</span>
          </h1>
          <p className="mt-3 text-sm text-muted-foreground max-w-2xl leading-relaxed">
            Tell the Copilot your <b>exploitation type</b>, <b>preferred region</b>, and <b>budget</b>.
            The User Profile Agent collects the profile, the Orchestrator retrieves the top-3 plots
            from PostgreSQL, the Financial / Risk Agent runs projections, and the Final Decision Agent
            picks a winner. Every step shows up in the panels below.
          </p>
          {profile && (
            <div className="mt-4 inline-flex items-center gap-3 text-[11px] font-mono border border-border rounded-sm px-3 py-1.5">
              <span className="text-muted-foreground">Current profile:</span>
              <span><b>{profile.exploitation_type}</b></span>
              {profile.preferred_region && <span>· {profile.preferred_region}</span>}
              {profile.budget != null && <span>· €{(profile.budget / 1e6).toFixed(2)}M budget</span>}
              {!profile.profile_completed && <span className="text-warning">· incomplete</span>}
            </div>
          )}
        </div>
      </section>

      <section className="grid lg:grid-cols-[1fr_420px] gap-px bg-border flex-1 border-b border-border">
        <div className="bg-background relative min-h-[520px]">
          <div className="absolute top-3 left-3 z-[400] terminal-panel px-3 py-1.5 rounded-sm">
            <div className="terminal-label">Sector Map · Hellas</div>
          </div>
          <PlotMap highlightIds={highlightIds} />
        </div>

        <aside className="bg-background p-4 space-y-3 overflow-y-auto max-h-[80vh]">
          <div className="terminal-label">// Plot Index</div>
          {plots.map((p) => {
            const top = bestScore(p);
            const hl = highlightIds.includes(p.property_id);
            return (
              <Link
                key={p.property_id}
                to="/plots/$plotId"
                params={{ plotId: p.property_id }}
                className={
                  "block terminal-panel p-4 rounded-sm hover:border-primary transition-colors group " +
                  (hl ? "border-primary" : "")
                }
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="text-base font-bold tracking-wide">{p.plot_name}</div>
                    <div className="terminal-label">{p.region}</div>
                  </div>
                  <div className={
                    "text-2xl font-bold terminal-value " +
                    (top.value >= 75 ? "text-positive" : top.value >= 50 ? "text-warning" : "text-negative")
                  }>
                    {top.value.toFixed(0)}
                  </div>
                </div>
                <div className="text-[11px] text-muted-foreground tracking-wider uppercase mb-3 font-mono">
                  Best fit: {top.label}
                </div>
                <div className="flex items-center justify-between text-[11px] text-primary group-hover:translate-x-1 transition-transform">
                  <span className="tracking-wider uppercase">Open Brief</span>
                  <ArrowRight className="w-3 h-3" />
                </div>
              </Link>
            );
          })}
        </aside>
      </section>

      <section className="px-6 py-8 border-t border-border">
        <div className="max-w-7xl mx-auto space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="terminal-label mb-1">// Agent reasoning</div>
              <h2 className="text-xl font-bold tracking-tight">Financial / Risk · Final Decision</h2>
            </div>
            <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
              <TrendingUp className="w-3.5 h-3.5" />
              Streamed live from the Orchestrator
            </div>
          </div>
          <AgentTabs />
        </div>
      </section>

      <Chatbot />
    </div>
  );
}

function Ticker({ plots }: { plots: Property[] }) {
  if (plots.length === 0) return null;
  return (
    <div className="border-b border-border bg-card/40 overflow-hidden">
      <div className="flex items-center gap-8 px-6 py-2 text-[11px] font-mono whitespace-nowrap overflow-x-auto">
        {plots.map((p) => {
          const top = bestScore(p);
          return (
            <div key={p.property_id} className="flex items-center gap-2">
              <span className="text-muted-foreground tracking-widest">{p.plot_name.toUpperCase()}</span>
              <span className="terminal-value text-foreground">€{(p.price_eur / 1e6).toFixed(2)}M</span>
              <span className={top.value >= 75 ? "text-positive" : top.value >= 50 ? "text-warning" : "text-negative"}>
                ▲ {top.value.toFixed(0)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
