/**
 * Agent reasoning tabs.
 *
 * Two tabs: Financial Potential / Risk + Final Decision. Both read from the
 * global session context. Empty / loading placeholders before the orchestrator
 * has produced the corresponding JSON.
 */
import { useState } from "react";
import {
  ArrowRight, BadgeCheck, Calculator, ShieldAlert, Sparkles, TrendingUp, TrendingDown,
} from "lucide-react";

import { useSession } from "../store";
import type {
  FinalRecommendation, FinancialAnalysisItem, Property,
} from "../types";

type Tab = "financial" | "decision";

export function AgentTabs() {
  const [tab, setTab] = useState<Tab>("financial");
  const { financial, decision, candidates, stage } = useSession();

  return (
    <section className="terminal-panel rounded-md">
      <div className="flex border-b border-border text-xs tracking-widest uppercase font-mono">
        <TabBtn icon={<Calculator className="w-3.5 h-3.5" />} active={tab === "financial"} onClick={() => setTab("financial")}>
          Financial / Risk Agent
        </TabBtn>
        <TabBtn icon={<BadgeCheck className="w-3.5 h-3.5" />} active={tab === "decision"} onClick={() => setTab("decision")}>
          Final Decision Agent
        </TabBtn>
        <div className="flex-1" />
        <div className="px-4 py-3 text-[10px] text-muted-foreground self-center">
          stage · <span className="terminal-value text-foreground">{stage}</span>
        </div>
      </div>

      <div className="p-4">
        {tab === "financial" ? (
          <FinancialTab items={financial?.financial_analysis} candidates={candidates} />
        ) : (
          <DecisionTab decision={decision} candidates={candidates} />
        )}
      </div>
    </section>
  );
}

function TabBtn({
  active, onClick, icon, children,
}: { active: boolean; onClick: () => void; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={
        "px-4 py-3 flex items-center gap-2 border-b-2 transition-colors " +
        (active
          ? "border-primary text-foreground bg-card"
          : "border-transparent text-muted-foreground hover:text-foreground")
      }
    >
      {icon} {children}
    </button>
  );
}

// ---------------------------------------------------------------------------

function FinancialTab({ items, candidates }: {
  items: FinancialAnalysisItem[] | undefined;
  candidates: Property[];
}) {
  if (!items || items.length === 0) {
    return <Placeholder
      icon={<Calculator className="w-5 h-5" />}
      title="Awaiting financial analysis"
      body="Once a profile is collected and candidates are retrieved, the Financial Potential / Risk Agent will fill this tab with capex, opex, revenue, payback, and ranked risks per candidate plot."
    />;
  }
  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
      {items.map((it) => {
        const candidate = candidates.find((c) => c.property_id === it.property_id);
        return (
          <article key={it.property_id} className="border border-border rounded-md p-4 bg-card">
            <header className="flex items-start justify-between mb-2">
              <div>
                <div className="text-sm font-bold">{candidate?.plot_name ?? it.property_id}</div>
                <div className="terminal-label">{it.exploitation_type}</div>
              </div>
              <RiskBadge level={it.risk_level} />
            </header>

            <div className="grid grid-cols-2 gap-2 text-[11px] mb-3">
              <Metric label="CAPEX"    value={`€${fmtK(it.estimated_initial_investment_eur)}`} />
              <Metric label="Revenue/yr" value={`€${fmtK(it.estimated_annual_revenue_eur)}`} />
              <Metric label="Opex/yr"  value={`€${fmtK(it.estimated_annual_operating_cost_eur)}`} />
              <Metric label="Net/yr"   value={`€${fmtK(it.estimated_net_annual_profit_eur)}`} accent />
              <Metric label="Payback"  value={`${it.estimated_payback_period_years.toFixed(1)} yrs`} accent />
            </div>

            <Section title="Risks" icon={<TrendingDown className="w-3 h-3 text-negative" />}>
              {it.risk_factors.map((r, i) => <li key={i}>{r}</li>)}
            </Section>

            <Section title="Opportunities" icon={<TrendingUp className="w-3 h-3 text-positive" />}>
              {it.opportunities.map((r, i) => <li key={i}>{r}</li>)}
            </Section>

            <p className="text-xs text-muted-foreground mt-3 leading-relaxed border-t border-border pt-2">
              {it.user_friendly_summary}
            </p>
          </article>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------

function DecisionTab({ decision, candidates }: {
  decision: FinalRecommendation | null;
  candidates: Property[];
}) {
  if (!decision) {
    return <Placeholder
      icon={<BadgeCheck className="w-5 h-5" />}
      title="Awaiting final decision"
      body="The Final Decision Agent compares the top candidates after the Financial / Risk Agent runs. It picks one winner, ranks the rest, and explains why."
    />;
  }
  const winner = candidates.find((c) => c.property_id === decision.final_recommendation.recommended_property_id);
  return (
    <div className="grid lg:grid-cols-[1fr_320px] gap-4">
      <div className="space-y-4">
        <div className="border border-primary rounded-md p-4 bg-card">
          <div className="flex items-center gap-2 terminal-label">
            <Sparkles className="w-3.5 h-3.5 text-primary" /> Winner
          </div>
          <div className="text-xl font-bold mt-1">{winner?.plot_name ?? decision.final_recommendation.recommended_property_id}</div>
          <div className="text-xs text-muted-foreground">
            Confidence: <span className="terminal-value font-bold">
              {(decision.final_recommendation.confidence * 100).toFixed(0)}%
            </span>
            {winner && <> · {winner.region}</>}
          </div>
          <p className="text-sm leading-relaxed mt-3">{decision.final_recommendation.reasoning_summary}</p>
          <div className="grid md:grid-cols-2 gap-3 mt-4">
            <Section title="Main reasons" icon={<TrendingUp className="w-3 h-3 text-positive" />}>
              {decision.final_recommendation.main_reasons.map((r, i) => <li key={i}>{r}</li>)}
            </Section>
            <Section title="Possible concerns" icon={<ShieldAlert className="w-3 h-3 text-warning" />}>
              {decision.final_recommendation.possible_concerns.map((r, i) => <li key={i}>{r}</li>)}
            </Section>
          </div>
        </div>

        <div className="border border-border rounded-md p-4 bg-card">
          <div className="terminal-label mb-2">Chatbot response</div>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{decision.chatbot_final_response}</p>
        </div>
      </div>

      <aside className="space-y-2">
        <div className="terminal-label">Full ranking</div>
        {decision.ranked_properties.map((r) => {
          const c = candidates.find((p) => p.property_id === r.property_id);
          return (
            <div key={r.property_id} className="border border-border rounded-sm p-3 bg-card">
              <div className="flex items-center justify-between mb-1">
                <div className="text-xs font-mono text-muted-foreground">#{r.rank}</div>
                <div className="text-xs font-bold">{c?.plot_name ?? r.property_id}</div>
              </div>
              <div className="text-[11px] text-muted-foreground leading-relaxed">{r.short_explanation}</div>
            </div>
          );
        })}
      </aside>
    </div>
  );
}

// ---------------------------------------------------------------------------

function Placeholder({ icon, title, body }: { icon: React.ReactNode; title: string; body: string }) {
  return (
    <div className="flex items-start gap-3 p-6 border border-dashed border-border rounded-md text-muted-foreground">
      <div className="text-primary">{icon}</div>
      <div>
        <div className="text-sm font-semibold text-foreground">{title}</div>
        <p className="text-xs mt-1 leading-relaxed max-w-xl">{body}</p>
      </div>
    </div>
  );
}

function Metric({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="border border-border rounded-sm p-2">
      <div className="terminal-label">{label}</div>
      <div className={"text-sm terminal-value font-bold " + (accent ? "text-primary" : "")}>{value}</div>
    </div>
  );
}

function RiskBadge({ level }: { level: "low" | "medium" | "high" }) {
  const cls = level === "low"    ? "text-positive border-positive"
            : level === "medium" ? "text-warning  border-warning"
            :                      "text-negative border-negative";
  return (
    <div className={"text-[10px] tracking-widest uppercase font-mono px-2 py-1 border rounded-sm " + cls}>
      {level}
    </div>
  );
}

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div>
      <div className="terminal-label flex items-center gap-1.5 mb-1">{icon} {title}</div>
      <ul className="text-[11px] leading-relaxed list-disc list-inside text-muted-foreground space-y-0.5">
        {children}
      </ul>
    </div>
  );
}

function fmtK(n: number): string {
  if (!Number.isFinite(n)) return "—";
  if (Math.abs(n) >= 1_000_000) return (n / 1_000_000).toFixed(2) + "M";
  if (Math.abs(n) >= 1_000)     return (n / 1_000).toFixed(0) + "k";
  return n.toFixed(0);
}

export function NextStepHint() {
  return (
    <div className="text-[11px] text-muted-foreground flex items-center gap-1.5">
      Ask the copilot follow-ups · "why this one?" · "compare 1 and 2" · "what changes if my budget doubles?"
      <ArrowRight className="w-3 h-3" />
    </div>
  );
}
